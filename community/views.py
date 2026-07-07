from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_requerido
from tracking.utils import calcular_racha_actual
from .forms import PostForm, RecetaForm, FraseComunidadForm
from .models import (
    Post, Reaccion, Receta, Frase,
    CompaneraDeCompromiso, MensajeCompanera,
    ItemRetoSemanal,
)
from .utils import (
    pareja_activa_de, buscar_companera_compatible, emparejar,
    marcar_item_reto_completado, total_puntos,
)

Usuario = get_user_model()


@login_required
def feed(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.usuario = request.user
            post.save()
            messages.success(request, "¡Publicado!")
            return redirect('community:feed')
    else:
        form = PostForm()

    posts = Post.objects.select_related('usuario').prefetch_related('reacciones')[:50]
    return render(request, 'community/feed.html', {'form': form, 'posts': posts, 'emojis': Reaccion.EMOJI_CHOICES})


@login_required
def reaccionar(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    emoji = request.POST.get('emoji')
    if request.method == 'POST' and emoji in dict(Reaccion.EMOJI_CHOICES):
        Reaccion.objects.update_or_create(
            post=post, usuario=request.user, defaults={'emoji': emoji}
        )
    return redirect('community:feed')


@login_required
def recetas_lista(request):
    categoria = request.GET.get('categoria', '')
    recetas = Receta.objects.aprobados().select_related('autor')
    if categoria:
        recetas = recetas.filter(categoria=categoria)

    return render(request, 'community/recetas_lista.html', {
        'recetas': recetas,
        'categorias': Receta.CATEGORIA_CHOICES,
        'categoria_activa': categoria,
    })


@login_required
def receta_nueva(request):
    if request.method == 'POST':
        form = RecetaForm(request.POST, request.FILES)
        if form.is_valid():
            receta = form.save(commit=False)
            receta.autor = request.user
            receta.aprobado = False  # Pasa por moderación antes de verse pública
            receta.save()
            messages.success(
                request,
                "¡Gracias por compartir tu receta! Se publicará en cuanto la revisemos."
            )
            return redirect('community:recetas_lista')
    else:
        form = RecetaForm()

    return render(request, 'community/receta_nueva.html', {'form': form})


@login_required
def receta_guardar(request, receta_id):
    receta = get_object_or_404(Receta, id=receta_id, aprobado=True)
    if receta.guardada_por.filter(id=request.user.id).exists():
        receta.guardada_por.remove(request.user)
    else:
        receta.guardada_por.add(request.user)
    return redirect('community:recetas_lista')


@login_required
def frases_lista(request):
    """
    Frases del sistema (personalizadas por momento) + frases que la
    comunidad ha compartido y ya fueron aprobadas.
    """
    momento = request.GET.get('momento', '')
    frases = Frase.objects.aprobados()
    if momento:
        frases = frases.filter(momento=momento)

    return render(request, 'community/frases_lista.html', {
        'frases': frases.order_by('-creado'),
        'momentos': Frase.MOMENTO_CHOICES,
        'momento_activo': momento,
    })


@login_required
def frase_nueva(request):
    if request.method == 'POST':
        form = FraseComunidadForm(request.POST)
        if form.is_valid():
            frase = form.save(commit=False)
            frase.origen = Frase.ORIGEN_COMUNIDAD
            frase.compartida_por = request.user
            frase.aprobado = False  # Pasa por moderación
            frase.save()
            messages.success(
                request,
                "¡Gracias por compartirla! Se mostrará al resto del club en cuanto la revisemos."
            )
            return redirect('community:frases_lista')
    else:
        form = FraseComunidadForm()

    return render(request, 'community/frase_nueva.html', {'form': form})


@login_required
def ranking(request):
    """Ranking por CONSTANCIA (racha actual), nunca por kilos perdidos. Se muestran también los puntos."""
    usuarias = list(Usuario.objects.all())
    tabla = sorted(
        (
            {'usuario': u, 'racha': calcular_racha_actual(u), 'puntos': total_puntos(u)}
            for u in usuarias
        ),
        key=lambda fila: fila['racha'],
        reverse=True,
    )
    return render(request, 'community/ranking.html', {'tabla': tabla[:50]})


@login_required
def marcar_item_completado(request, item_id):
    item = get_object_or_404(ItemRetoSemanal, id=item_id)
    if request.method == 'POST':
        marcar_item_reto_completado(request.user, item)
        messages.success(request, f"¡Completaste \"{item.texto}\"! +{item.puntos} puntos.")
    return redirect('tracking:dashboard')


@login_required
def mi_companera(request):
    pareja = pareja_activa_de(request.user)

    companera = None
    mensajes = []

    if pareja:
        companera = pareja.usuario_2 if pareja.usuario_1 == request.user else pareja.usuario_1
        mensajes = pareja.mensajes.select_related('remitente')

        if request.method == 'POST' and request.POST.get('accion') == 'mensaje':
            texto = request.POST.get('texto', '').strip()
            if texto:
                MensajeCompanera.objects.create(pareja=pareja, remitente=request.user, texto=texto)
                return redirect('community:mi_companera')

    elif request.method == 'POST' and request.POST.get('accion') == 'buscar':
        # Emparejamiento al vuelo: mismo horario + objetivo, o el mejor disponible.
        candidata = buscar_companera_compatible(request.user)
        if candidata:
            emparejar(request.user, candidata)
            nombre = candidata.nombre_para_mostrar or candidata.username
            messages.success(request, f"¡Listo! Te emparejamos con {nombre}.")
        else:
            messages.info(
                request,
                "Por ahora no hay nadie disponible con un perfil compatible. "
                "En cuanto se registre alguien más te avisamos."
            )
        return redirect('community:mi_companera')

    return render(request, 'community/mi_companera.html', {
        'companera': companera, 'mensajes': mensajes, 'pareja': pareja,
    })


@admin_requerido
def socios_lista(request):
    """Panel del administrador con todos los socios del club."""
    socios = Usuario.objects.all().order_by('-date_joined')
    return render(request, 'community/socios_lista.html', {'socios': socios})


@admin_requerido
def socio_banear(request, socio_id):
    """
    'Banear' = desactivar la cuenta (is_active=False): la socia deja de
    poder iniciar sesión, pero su historial y datos se conservan. Se puede
    revertir (reactivar) volviendo a entrar aquí.
    """
    socio = get_object_or_404(Usuario, id=socio_id)

    if request.method == 'POST':
        if socio == request.user:
            messages.error(request, "No puedes banearte a ti misma.")
        elif socio.is_superuser and not request.user.is_superuser:
            messages.error(request, "No tienes permiso para banear a otro administrador.")
        else:
            socio.is_active = not socio.is_active
            socio.save(update_fields=['is_active'])
            nombre = socio.nombre_para_mostrar or socio.username
            if socio.is_active:
                messages.success(request, f"Se reactivó la cuenta de {nombre}.")
            else:
                messages.success(request, f"Se baneó la cuenta de {nombre}.")

    return redirect('community:socios_lista')


@admin_requerido
def socio_eliminar(request, socio_id):
    """Elimina definitivamente la cuenta de un socio (pide confirmación)."""
    socio = get_object_or_404(Usuario, id=socio_id)

    if request.method == 'POST':
        if socio == request.user:
            messages.error(request, "No puedes eliminar tu propia cuenta desde aquí.")
        elif socio.is_superuser and not request.user.is_superuser:
            messages.error(request, "No tienes permiso para eliminar a otro administrador.")
        else:
            nombre = socio.nombre_para_mostrar or socio.username
            socio.delete()
            messages.success(request, f"Se eliminó la cuenta de {nombre}.")
        return redirect('community:socios_lista')

    return render(request, 'community/socio_eliminar_confirmar.html', {'socio': socio})
