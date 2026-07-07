from datetime import timedelta
from django.utils import timezone
from .models import RegistroDiario


def calcular_racha_actual(usuario):
    """
    Cuenta cuántos días consecutivos ha entrenado la usuaria, contando
    hacia atrás desde hoy (o desde ayer, si hoy todavía no registra nada).

    Esta es la función más importante del sistema: de ella depende
    "NO ROMPAS LA CADENA", el ranking por constancia y varias medallas.
    """
    hoy = timezone.now().date()

    registros = {
        r.fecha: r.entreno
        for r in RegistroDiario.objects.filter(usuario=usuario, fecha__lte=hoy)
    }

    # Si hoy todavía no hay registro, empezamos a contar desde ayer
    # (para no "romper" la racha solo porque todavía no ha entrado hoy).
    fecha_cursor = hoy if hoy in registros else hoy - timedelta(days=1)

    racha = 0
    while registros.get(fecha_cursor) is True:
        racha += 1
        fecha_cursor -= timedelta(days=1)

    return racha


def calcular_dias_totales_entrenados(usuario):
    """Total histórico de días entrenados (para medallas tipo '100 entrenamientos')."""
    return RegistroDiario.objects.filter(usuario=usuario, entreno=True).count()


def registro_de_hoy(usuario):
    """Regresa el RegistroDiario de hoy si ya existe, o None."""
    hoy = timezone.now().date()
    return RegistroDiario.objects.filter(usuario=usuario, fecha=hoy).first()
