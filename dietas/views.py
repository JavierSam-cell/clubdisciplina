from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.decorators import admin_requerido
from .forms import DietaForm, DietaComidaFormSet
from .models import Dieta


@login_required
def dietas_lista(request):
    usuario = request.user

    # --- Dietas recomendadas según su perfil (lo que ya eligió al registrarse) ---
    recomendadas = Dieta.objects.filter(
        preferencia=usuario.preferencia_alimenticia,
        presupuesto=usuario.presupuesto_comida,
        objetivo=usuario.objetivo,
    )

    # --- Filtros manuales para explorar todo el catálogo ---
    categoria = request.GET.get('categoria', '')
    preferencia = request.GET.get('preferencia', '')
    presupuesto = request.GET.get('presupuesto', '')

    todas = Dieta.objects.all()
    if categoria:
        todas = todas.filter(categoria=categoria)
    if preferencia:
        todas = todas.filter(preferencia=preferencia)
    if presupuesto:
        todas = todas.filter(presupuesto=presupuesto)

    return render(request, 'dietas/dietas_lista.html', {
        'recomendadas': recomendadas,
        'todas': todas,
        'categorias': Dieta.CATEGORIA_CHOICES,
        'preferencias': Dieta.PREFERENCIA_CHOICES,
        'presupuestos': Dieta.PRESUPUESTO_CHOICES,
        'categoria_activa': categoria,
        'preferencia_activa': preferencia,
        'presupuesto_activo': presupuesto,
    })


@login_required
def dieta_detalle(request, dieta_id):
    dieta = get_object_or_404(Dieta, id=dieta_id)
    comidas = dieta.dieta_comidas.select_related('comida').order_by('orden')
    return render(request, 'dietas/dieta_detalle.html', {'dieta': dieta, 'comidas': comidas})


@admin_requerido
def dieta_nueva(request):
    """
    Solo el administrador puede crear dietas nuevas. En cuanto se guarda,
    queda visible para toda la comunidad (no hay ningún filtro por usuario
    en dietas_lista, así que todas las socias la ven de inmediato).
    """
    if request.method == 'POST':
        form = DietaForm(request.POST)
        if form.is_valid():
            dieta = form.save(commit=False)
            formset = DietaComidaFormSet(request.POST, instance=dieta)
            if formset.is_valid():
                dieta.save()
                formset.instance = dieta
                formset.save()
                messages.success(
                    request,
                    f"¡Dieta '{dieta.nombre}' creada! Ya está visible para toda la comunidad."
                )
                return redirect('dietas:dieta_detalle', dieta.id)
        else:
            formset = DietaComidaFormSet(request.POST)
    else:
        form = DietaForm()
        formset = DietaComidaFormSet()

    return render(request, 'dietas/dieta_nueva.html', {'form': form, 'formset': formset})
