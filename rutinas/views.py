from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_requerido
from .forms import RutinaForm, RutinaEjercicioFormSet
from .models import Rutina, Ejercicio


@login_required
def rutinas_lista(request):
    usuario = request.user

    # --- Rutinas recomendadas según su perfil (lo que ya eligió al registrarse) ---
    recomendadas = Rutina.objects.filter(
        lugar=usuario.lugar_entreno,
        nivel=usuario.nivel,
        minutos_duracion__lte=usuario.minutos_disponibles + 10,
    )

    # --- Filtros manuales para explorar todo el catálogo ---
    lugar = request.GET.get('lugar', '')
    nivel = request.GET.get('nivel', '')
    categoria = request.GET.get('categoria', '')

    todas = Rutina.objects.all()
    if lugar:
        todas = todas.filter(lugar=lugar)
    if nivel:
        todas = todas.filter(nivel=nivel)
    if categoria:
        todas = todas.filter(categoria=categoria)

    return render(request, 'rutinas/rutinas_lista.html', {
        'recomendadas': recomendadas,
        'todas': todas,
        'lugares': Rutina.LUGAR_CHOICES,
        'niveles': Rutina.NIVEL_CHOICES,
        'categorias': Rutina.CATEGORIA_CHOICES,
        'lugar_activo': lugar,
        'nivel_activo': nivel,
        'categoria_activa': categoria,
    })


@login_required
def rutina_detalle(request, rutina_id):
    rutina = get_object_or_404(Rutina, id=rutina_id)
    pasos = rutina.rutina_ejercicios.select_related('ejercicio').order_by('orden')
    return render(request, 'rutinas/rutina_detalle.html', {'rutina': rutina, 'pasos': pasos})


@login_required
def biblioteca(request):
    grupo = request.GET.get('grupo', '')
    ejercicios = Ejercicio.objects.all()
    if grupo:
        ejercicios = ejercicios.filter(grupo_muscular=grupo)

    return render(request, 'rutinas/biblioteca.html', {
        'ejercicios': ejercicios,
        'grupos': Ejercicio.GRUPO_CHOICES,
        'grupo_activo': grupo,
    })


@admin_requerido
def rutina_nueva(request):
    """
    Solo el administrador puede crear rutinas nuevas. En cuanto se guarda,
    queda visible para toda la comunidad (no hay ningún filtro por usuario
    en rutinas_lista, así que todas las socias la ven de inmediato).
    """
    if request.method == 'POST':
        form = RutinaForm(request.POST)
        if form.is_valid():
            rutina = form.save(commit=False)
            formset = RutinaEjercicioFormSet(request.POST, instance=rutina)
            if formset.is_valid():
                rutina.save()
                formset.instance = rutina
                formset.save()
                messages.success(
                    request,
                    f"¡Rutina '{rutina.nombre}' creada! Ya está visible para toda la comunidad."
                )
                return redirect('rutinas:rutina_detalle', rutina.id)
        else:
            formset = RutinaEjercicioFormSet(request.POST)
    else:
        form = RutinaForm()
        formset = RutinaEjercicioFormSet()

    return render(request, 'rutinas/rutina_nueva.html', {'form': form, 'formset': formset})
