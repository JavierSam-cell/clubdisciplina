from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from .forms import RegistroForm, PerfilForm


def landing(request):
    """Página principal pública. Si ya inició sesión, la mandamos al dashboard."""
    if request.user.is_authenticated:
        return redirect('tracking:dashboard')
    return render(request, 'accounts/landing.html')


def registro(request):
    """Cuestionario inicial + creación de cuenta, en un solo paso."""
    if request.user.is_authenticated:
        return redirect('tracking:dashboard')

    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save()
            login(request, usuario)
            messages.success(
                request,
                f"¡Bienvenida, {usuario.nombre_para_mostrar}! Hoy es el día 1 de tu compromiso."
            )
            return redirect('tracking:dashboard')
    else:
        form = RegistroForm()

    return render(request, 'accounts/registro.html', {'form': form})


@login_required
def mi_cuenta(request):
    """Editar datos del perfil ya con la cuenta creada."""
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Tu perfil se actualizó correctamente.")
            return redirect('accounts:mi_cuenta')
    else:
        form = PerfilForm(instance=request.user)

    return render(request, 'accounts/mi_cuenta.html', {'form': form})
