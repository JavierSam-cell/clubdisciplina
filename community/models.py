from django.conf import settings
from django.db import models
from django.utils import timezone


class ContenidoModeradoQuerySet(models.QuerySet):
    """Queryset reutilizable: solo trae contenido ya aprobado por moderación."""
    def aprobados(self):
        return self.filter(aprobado=True)


class Post(models.Model):
    """Publicación en el feed de comunidad: comida, entrenamiento o logro."""
    TIPO_COMIDA = 'comida'
    TIPO_ENTRENAMIENTO = 'entrenamiento'
    TIPO_LOGRO = 'logro'
    TIPO_CHOICES = [
        (TIPO_COMIDA, 'Comida'),
        (TIPO_ENTRENAMIENTO, 'Entrenamiento'),
        (TIPO_LOGRO, 'Logro'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts'
    )
    tipo = models.CharField(max_length=15, choices=TIPO_CHOICES)
    texto = models.CharField(max_length=500, blank=True)
    imagen = models.ImageField(upload_to='posts/%Y/%m/', blank=True, null=True)
    creado = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f"Post de {self.usuario} ({self.tipo})"


class Reaccion(models.Model):
    """Reacción rápida a un post (🔥, 💪, etc.) — baja fricción para interactuar."""
    EMOJI_FUEGO = '🔥'
    EMOJI_FUERZA = '💪'
    EMOJI_APLAUSO = '👏'
    EMOJI_CHOICES = [
        (EMOJI_FUEGO, 'Sigue así'),
        (EMOJI_FUERZA, 'Yo también entrené hoy'),
        (EMOJI_APLAUSO, 'Felicidades'),
    ]
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reacciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    emoji = models.CharField(max_length=5, choices=EMOJI_CHOICES)

    class Meta:
        # Una persona solo puede reaccionar una vez por post (puede cambiar su emoji).
        unique_together = ('post', 'usuario')


class Receta(models.Model):
    """
    Receta compartida por cualquier usuaria (ej. el cóctel de frutas de Juanita).
    Contenido abierto, pero pasa por moderación antes de verse públicamente.
    """
    CATEGORIA_CHOICES = [
        ('economica', 'Económica'),
        ('vegetariana', 'Vegetariana'),
        ('oficina', 'Para oficina'),
        ('mexicana', 'Mexicana'),
        ('rapida', 'Rápida'),
        ('familiar', 'Familiar'),
        ('meal_prep', 'Meal prep / domingo'),
        ('flexible', 'Flexible (80/20)'),
        ('snack', 'Snack / colación'),
    ]

    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='recetas'
    )
    titulo = models.CharField(max_length=150)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    ingredientes = models.TextField(help_text="Un ingrediente por línea.")
    preparacion = models.TextField()
    imagen = models.ImageField(upload_to='recetas/%Y/%m/', blank=True, null=True)
    creado = models.DateTimeField(default=timezone.now)

    # --- Moderación: nada se ve público hasta ser revisado ---
    aprobado = models.BooleanField(default=False)
    revisado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='recetas_revisadas'
    )

    # Usuarias que la guardaron en "mis favoritas"
    guardada_por = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='recetas_favoritas', blank=True
    )

    objects = ContenidoModeradoQuerySet.as_manager()

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return self.titulo


class Frase(models.Model):
    """
    Banco de frases. Dos orígenes posibles:
      - 'sistema': frases personalizadas que se disparan según el momento
        de la usuaria (día 1, racha rota, estancamiento, domingo...).
      - 'comunidad': frases que una usuaria compartió (ej. Edith vio una
        frase bonita y la subió). Pasan por moderación antes de mostrarse.
    """
    ORIGEN_SISTEMA = 'sistema'
    ORIGEN_COMUNIDAD = 'comunidad'
    ORIGEN_CHOICES = [
        (ORIGEN_SISTEMA, 'Sistema (personalizada por momento)'),
        (ORIGEN_COMUNIDAD, 'Compartida por la comunidad'),
    ]

    MOMENTO_DIA_1 = 'dia_1'
    MOMENTO_RACHA_ACTIVA = 'racha_activa'
    MOMENTO_RACHA_ROTA = 'racha_rota'
    MOMENTO_ESTANCAMIENTO = 'estancamiento'
    MOMENTO_DOMINGO = 'domingo'
    MOMENTO_GENERAL = 'general'
    MOMENTO_CHOICES = [
        (MOMENTO_DIA_1, 'Arrancando (día 1-3)'),
        (MOMENTO_RACHA_ACTIVA, 'Racha activa (7+ días)'),
        (MOMENTO_RACHA_ROTA, 'Día después de faltar'),
        (MOMENTO_ESTANCAMIENTO, 'Estancamiento (2-3 semanas sin cambio)'),
        (MOMENTO_DOMINGO, 'Domingo (planeación de la semana)'),
        (MOMENTO_GENERAL, 'General / cualquier momento'),
    ]

    texto = models.CharField(max_length=300)
    origen = models.CharField(max_length=12, choices=ORIGEN_CHOICES, default=ORIGEN_SISTEMA)
    momento = models.CharField(max_length=20, choices=MOMENTO_CHOICES, default=MOMENTO_GENERAL)

    # Solo aplica si origen == comunidad
    compartida_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='frases_compartidas'
    )
    aprobado = models.BooleanField(
        default=True,  # Las frases del sistema entran aprobadas desde el admin.
        help_text="Para frases de comunidad, empieza en False hasta moderar."
    )
    creado = models.DateTimeField(default=timezone.now)

    objects = ContenidoModeradoQuerySet.as_manager()

    def __str__(self):
        return self.texto[:60]


class CompaneraDeCompromiso(models.Model):
    """
    Buddy system: empareja a dos usuarias con objetivo/horario similar.
    Ambas ven el progreso de la otra y se pueden mandar ánimo.
    """
    usuario_1 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+'
    )
    usuario_2 = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='+'
    )
    fecha_emparejamiento = models.DateField(default=timezone.now)
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ('usuario_1', 'usuario_2')

    def __str__(self):
        return f"{self.usuario_1} <-> {self.usuario_2}"


class MensajeCompanera(models.Model):
    """Mensaje corto entre compañeras de compromiso (no un chat completo, algo simple)."""
    pareja = models.ForeignKey(
        CompaneraDeCompromiso, on_delete=models.CASCADE, related_name='mensajes'
    )
    remitente = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    texto = models.CharField(max_length=300)
    creado = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['creado']


class OpcionRetoBiblioteca(models.Model):
    """
    Biblioteca de retos posibles, agrupados por categoría (agua, entrenamiento,
    alimentación, mental, foto de progreso...). Cada lunes el sistema elige
    automáticamente una opción de cada categoría activa para armar la semana,
    así los retos no se repiten siempre y no hay que crearlos a mano.
    """
    CATEGORIA_AGUA = 'agua'
    CATEGORIA_ENTRENAMIENTO = 'entrenamiento'
    CATEGORIA_ALIMENTACION = 'alimentacion'
    CATEGORIA_MENTAL = 'mental'
    CATEGORIA_FOTO_PROGRESO = 'foto_progreso'
    CATEGORIA_CHOICES = [
        (CATEGORIA_AGUA, '💧 Agua'),
        (CATEGORIA_ENTRENAMIENTO, '🏋️ Entrenamiento'),
        (CATEGORIA_ALIMENTACION, '🥗 Alimentación'),
        (CATEGORIA_MENTAL, '🧘 Mental'),
        (CATEGORIA_FOTO_PROGRESO, '📷 Foto de progreso'),
    ]

    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    texto = models.CharField(max_length=150, help_text="Ej. 'Entrena 4 días' o 'Toma 2 litros de agua'.")
    puntos = models.PositiveSmallIntegerField(default=20)
    activo = models.BooleanField(
        default=True,
        help_text="Desactívala para dejar de usarla en semanas nuevas sin borrar el historial ya generado."
    )

    class Meta:
        ordering = ['categoria', 'texto']

    def __str__(self):
        return f"[{self.get_categoria_display()}] {self.texto} ({self.puntos} pts)"


class RetoSemanal(models.Model):
    """
    Una semana de retos del club: agrupa un ítem elegido de cada categoría
    (ver ItemRetoSemanal). Normalmente se genera sola cada lunes con el
    comando `generar_reto_semanal`, pero también se puede crear a mano
    desde el admin si se quiere forzar algo puntual.
    """
    fecha_inicio = models.DateField(unique=True)
    fecha_fin = models.DateField()
    generado_automaticamente = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_inicio']

    def esta_activo(self):
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_fin

    def total_puntos_disponibles(self):
        return sum(item.puntos for item in self.items.all())

    def __str__(self):
        return f"Semana de retos {self.fecha_inicio} – {self.fecha_fin}"


class ItemRetoSemanal(models.Model):
    """Un reto concreto dentro de la semana (normalmente uno por categoría)."""
    reto_semanal = models.ForeignKey(RetoSemanal, on_delete=models.CASCADE, related_name='items')
    categoria = models.CharField(max_length=20, choices=OpcionRetoBiblioteca.CATEGORIA_CHOICES)
    opcion = models.ForeignKey(
        OpcionRetoBiblioteca, on_delete=models.SET_NULL, null=True, blank=True, related_name='usos'
    )
    # Se copian desde la OpcionRetoBiblioteca al generar la semana, para que
    # el historial no cambie si luego se edita o desactiva la opción original.
    texto = models.CharField(max_length=150)
    puntos = models.PositiveSmallIntegerField(default=20)

    class Meta:
        ordering = ['categoria']

    def __str__(self):
        return f"{self.texto} ({self.puntos} pts)"


class ParticipacionItemReto(models.Model):
    """Marca si una usuaria completó un ítem concreto del reto de la semana."""
    item = models.ForeignKey(ItemRetoSemanal, on_delete=models.CASCADE, related_name='participaciones')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    completado = models.BooleanField(default=False)
    fecha_completado = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('item', 'usuario')

    def __str__(self):
        return f"{self.usuario} - {self.item} ({'✔' if self.completado else '—'})"


class PuntosEvento(models.Model):
    """
    Ledger de puntos: cada fila es un evento que sumó puntos a una usuaria
    (completar un ítem de reto, bono de racha...). El total acumulado se
    calcula sumando esta tabla, y sirve también como auditoría de en qué
    se ganó cada punto.
    """
    MOTIVO_RETO = 'reto'
    MOTIVO_RACHA = 'racha'
    MOTIVO_CHOICES = [
        (MOTIVO_RETO, 'Reto semanal completado'),
        (MOTIVO_RACHA, 'Bono de racha'),
    ]

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='puntos_eventos'
    )
    puntos = models.SmallIntegerField()
    motivo = models.CharField(max_length=10, choices=MOTIVO_CHOICES)
    detalle = models.CharField(max_length=200, blank=True)
    creado = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['-creado']

    def __str__(self):
        return f"{self.usuario} +{self.puntos} pts ({self.motivo})"
