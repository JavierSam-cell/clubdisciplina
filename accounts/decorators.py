from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def admin_requerido(view_func):
    """
    Igual que @login_required, pero además exige que sea administrador
    (staff). Se usa para todo lo que solo el admin del club puede hacer:
    crear rutinas/dietas nuevas, banear o eliminar socios, etc.
    """
    @login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_staff:
            messages.error(request, "Esta sección es solo para el administrador del club.")
            return redirect('tracking:dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper
