from django.conf import settings
from django.db import models
from django.utils import timezone


class RegistroDiario(models.Model):
    """
    Un check-in de un día. Esta es la tabla más importante del sistema:
    de aquí se calculan las rachas, el ranking por constancia y las medallas.
    """
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='registros'
    )
    fecha = models.DateField(default=timezone.now)

    entreno = models.BooleanField(
        default=False, help_text="¿Entrenó este día?"
    )
    minutos_entrenados = models.PositiveSmallIntegerField(null=True, blank=True)

    tomo_agua_meta = models.BooleanField(
        default=False, help_text="¿Cumplió su meta de agua del día?"
    )
    horas_sueno = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )

    peso_kg = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)
    cintura_cm = models.DecimalField(max_digits=5, decimal_places=1, null=True, blank=True)

    momento_dificil = models.CharField(
        max_length=255, blank=True,
        help_text="Respuesta libre: '¿qué fue lo más difícil hoy?'"
    )

    class Meta:
        # Solo puede haber UN registro por usuaria por día.
        unique_together = ('usuario', 'fecha')
        ordering = ['-fecha']

    def __str__(self):
        return f"{self.usuario} - {self.fecha} ({'entrenó' if self.entreno else 'no entrenó'})"


class Medalla(models.Model):
    """Catálogo de medallas disponibles (7 días, 30 días, primer kilo, etc.)."""
    nombre = models.CharField(max_length=100)
    descripcion = models.CharField(max_length=255)
    icono = models.CharField(
        max_length=10, default='🏅',
        help_text="Emoji o clase de ícono para mostrar."
    )
    # Tipo de condición para poder calcular automáticamente si se ganó.
    TIPO_RACHA_DIAS = 'racha_dias'
    TIPO_TOTAL_ENTRENAMIENTOS = 'total_entrenamientos'
    TIPO_KILOS_PERDIDOS = 'kilos_perdidos'
    TIPO_MANUAL = 'manual'
    TIPO_CHOICES = [
        (TIPO_RACHA_DIAS, 'Racha de días consecutivos'),
        (TIPO_TOTAL_ENTRENAMIENTOS, 'Total de entrenamientos acumulados'),
        (TIPO_KILOS_PERDIDOS, 'Kilos perdidos desde el inicio'),
        (TIPO_MANUAL, 'Otorgada manualmente'),
    ]
    tipo_condicion = models.CharField(max_length=25, choices=TIPO_CHOICES)
    valor_condicion = models.PositiveSmallIntegerField(
        help_text="Ej. 7 (para racha de 7 días), 100 (para 100 entrenamientos)."
    )

    def __str__(self):
        return self.nombre


class MedallaObtenida(models.Model):
    """Registro de qué medalla ganó cada usuaria y cuándo."""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='medallas_obtenidas'
    )
    medalla = models.ForeignKey(Medalla, on_delete=models.CASCADE)
    fecha_obtenida = models.DateField(default=timezone.now)

    class Meta:
        unique_together = ('usuario', 'medalla')

    def __str__(self):
        return f"{self.usuario} ganó {self.medalla}"


class FotoProgreso(models.Model):
    """Fotos de antes/después que sube la usuaria a su propio progreso (privado)."""
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='fotos_progreso'
    )
    imagen = models.ImageField(upload_to='progreso/%Y/%m/')
    fecha = models.DateField(default=timezone.now)
    nota = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['fecha']

    def __str__(self):
        return f"Foto de {self.usuario} - {self.fecha}"
