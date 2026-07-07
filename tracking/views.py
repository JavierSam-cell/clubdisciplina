from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone

from community.utils import (
    frase_para_usuario, mensaje_motivacional_dia, reto_semanal_activo,
    total_puntos, evaluar_bono_racha,
)
from community.models import ParticipacionItemReto
from .forms import RegistroDiarioForm, FotoProgresoForm
from .models import MedallaObtenida, FotoProgreso
from .utils import calcular_racha_actual, calcular_dias_totales_entrenados, registro_de_hoy


@login_required
def dashboard(request):
    usuario = request.user
    racha_actual = calcular_racha_actual(usuario)
    registro_hoy = registro_de_hoy(usuario)

    reto_activo = reto_semanal_activo()
    items_reto = []
    puntos_ganados_semana = 0
    puntos_totales_semana = 0
    if reto_activo:
        items = list(reto_activo.items.all())
        participaciones = {
            p.item_id: p for p in ParticipacionItemReto.objects.filter(
                item__in=items, usuario=usuario
            )
        }
        for item in items:
            participacion = participaciones.get(item.id)
            completado = bool(participacion and participacion.completado)
            items_reto.append({'item': item, 'completado': completado})
            puntos_totales_semana += item.puntos
            if completado:
                puntos_ganados_semana += item.puntos

    contexto = {
        'usuario': usuario,
        'dias_de_compromiso': usuario.dias_de_compromiso(),
        'racha_actual': racha_actual,
        'dias_totales_entrenados': calcular_dias_totales_entrenados(usuario),
        'registro_hoy': registro_hoy,
        'frase': frase_para_usuario(usuario),
        'mensaje_del_dia': mensaje_motivacional_dia(),
        'medallas_recientes': MedallaObtenida.objects.filter(usuario=usuario).order_by('-fecha_obtenida')[:5],
        'reto_activo': reto_activo,
        'items_reto': items_reto,
        'puntos_ganados_semana': puntos_ganados_semana,
        'puntos_totales_semana': puntos_totales_semana,
        'puntos_totales_historicos': total_puntos(usuario),
    }
    return render(request, 'tracking/dashboard.html', contexto)


@login_required
def check_in_hoy(request):
    """Formulario de 'check-in' del día: ¿entrenaste?, agua, sueño, peso..."""
    instancia = registro_de_hoy(request.user)

    if request.method == 'POST':
        form = RegistroDiarioForm(request.POST, instance=instancia)
        if form.is_valid():
            registro = form.save(commit=False)
            registro.usuario = request.user
            registro.fecha = timezone.now().date()
            registro.save()

            if registro.entreno:
                # El check-in ya es único por usuaria/día, así que esto se
                # evalúa como máximo una vez por cada vez que la racha
                # llega exactamente a un umbral (3, 7, 15, 30, 100...).
                evaluar_bono_racha(request.user, calcular_racha_actual(request.user))

            messages.success(request, "Registro de hoy guardado. ¡Así se hace!")
            return redirect('tracking:dashboard')
    else:
        form = RegistroDiarioForm(instance=instancia)

    return render(request, 'tracking/check_in.html', {'form': form})


@login_required
def fotos_progreso(request):
    """Galería privada de fotos de progreso: subir nuevas y ver todas las anteriores."""
    if request.method == 'POST':
        form = FotoProgresoForm(request.POST, request.FILES)
        if form.is_valid():
            foto = form.save(commit=False)
            foto.usuario = request.user
            foto.save()
            messages.success(request, "Foto de progreso guardada.")
            return redirect('tracking:fotos_progreso')
    else:
        form = FotoProgresoForm(initial={'fecha': timezone.now().date()})

    fotos = FotoProgreso.objects.filter(usuario=request.user).order_by('-fecha')

    return render(request, 'tracking/fotos_progreso.html', {
        'form': form,
        'fotos': fotos,
    })


@login_required
def comparacion_progreso(request):
    """Comparación lado a lado de dos fotos: 'antes' y 'después'."""
    fotos = FotoProgreso.objects.filter(usuario=request.user).order_by('fecha')

    antes_id = request.GET.get('antes')
    despues_id = request.GET.get('despues')

    foto_antes = fotos.filter(id=antes_id).first() if antes_id else fotos.first()
    foto_despues = fotos.filter(id=despues_id).first() if despues_id else fotos.last()

    return render(request, 'tracking/comparacion_progreso.html', {
        'fotos': fotos,
        'foto_antes': foto_antes,
        'foto_despues': foto_despues,
    })
