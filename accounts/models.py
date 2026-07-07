from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Usuario(AbstractUser):
    """
    Nuestro usuario personalizado. Extiende el usuario base de Django
    (que ya trae username, password, email, login, etc.) y le agrega
    todos los campos del cuestionario inicial que diseñaste.
    """

    # --- Elección del tono de mensajes (esto resuelve la duda de si
    # los mensajes deben ser "fuertes" o no: que cada quien elija) ---
    TONO_SUAVE = 'suave'
    TONO_DIRECTO = 'directo'
    TONO_CHOICES = [
        (TONO_SUAVE, 'Motivación cercana y comprensiva'),
        (TONO_DIRECTO, 'Directo y sin filtros'),
    ]
    tono_mensajes = models.CharField(
        max_length=10, choices=TONO_CHOICES, default=TONO_SUAVE,
        help_text="Cómo prefiere la usuaria que le hablemos en frases y notificaciones."
    )

    # --- Datos del cuestionario inicial ---
    nombre_para_mostrar = models.CharField(
        max_length=50, blank=True,
        help_text="Nombre con el que se le saluda en el dashboard (ej. 'María')."
    )
    edad = models.PositiveSmallIntegerField(null=True, blank=True)
    estatura_cm = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Estatura en centímetros."
    )

    peso_inicial_kg = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )
    cintura_inicial_cm = models.DecimalField(
        max_digits=5, decimal_places=1, null=True, blank=True
    )

    OBJETIVO_BAJAR_PESO = 'bajar_peso'
    OBJETIVO_TONIFICAR = 'tonificar'
    OBJETIVO_GANAR_MUSCULO = 'ganar_musculo'
    OBJETIVO_SALUD = 'salud_general'
    OBJETIVO_CHOICES = [
        (OBJETIVO_BAJAR_PESO, 'Bajar de peso'),
        (OBJETIVO_TONIFICAR, 'Tonificar'),
        (OBJETIVO_GANAR_MUSCULO, 'Ganar músculo'),
        (OBJETIVO_SALUD, 'Salud general / sentirme mejor'),
    ]
    objetivo = models.CharField(
        max_length=20, choices=OBJETIVO_CHOICES,
        default=OBJETIVO_SALUD,
    )

    LUGAR_CASA = 'casa'
    LUGAR_GIMNASIO = 'gimnasio'
    LUGAR_CHOICES = [
        (LUGAR_CASA, 'En casa'),
        (LUGAR_GIMNASIO, 'En gimnasio'),
    ]
    lugar_entreno = models.CharField(
        max_length=10, choices=LUGAR_CHOICES, default=LUGAR_CASA
    )

    NIVEL_PRINCIPIANTE = 'principiante'
    NIVEL_INTERMEDIO = 'intermedio'
    NIVEL_AVANZADO = 'avanzado'
    NIVEL_CHOICES = [
        (NIVEL_PRINCIPIANTE, 'Principiante'),
        (NIVEL_INTERMEDIO, 'Intermedio'),
        (NIVEL_AVANZADO, 'Avanzado'),
    ]
    nivel = models.CharField(
        max_length=15, choices=NIVEL_CHOICES, default=NIVEL_PRINCIPIANTE
    )

    minutos_disponibles = models.PositiveSmallIntegerField(
        default=30,
        help_text="Minutos disponibles por sesión (20, 30, 45, 60...)."
    )

    lesiones = models.TextField(
        blank=True,
        help_text="Lesiones o limitaciones físicas a tener en cuenta al sugerir rutinas."
    )

    HORARIO_MANANA = 'manana'
    HORARIO_TARDE = 'tarde'
    HORARIO_NOCHE = 'noche'
    HORARIO_VARIABLE = 'variable'
    HORARIO_CHOICES = [
        (HORARIO_MANANA, 'Mañana'),
        (HORARIO_TARDE, 'Tarde'),
        (HORARIO_NOCHE, 'Noche'),
        (HORARIO_VARIABLE, 'Variable / no tengo un horario fijo'),
    ]
    horario_preferido = models.CharField(
        max_length=10, choices=HORARIO_CHOICES, default=HORARIO_VARIABLE,
        help_text="Se usa, entre otras cosas, para emparejarte con una compañera de compromiso."
    )

    # --- Perfil alimenticio (para filtrar dietas, igual que rutinas) ---
    PREFERENCIA_OMNIVORO = 'omnivoro'
    PREFERENCIA_VEGETARIANA = 'vegetariana'
    PREFERENCIA_VEGANA = 'vegana'
    PREFERENCIA_SIN_GLUTEN = 'sin_gluten'
    PREFERENCIA_CHOICES = [
        (PREFERENCIA_OMNIVORO, 'Como de todo'),
        (PREFERENCIA_VEGETARIANA, 'Vegetariana'),
        (PREFERENCIA_VEGANA, 'Vegana'),
        (PREFERENCIA_SIN_GLUTEN, 'Sin gluten'),
    ]
    preferencia_alimenticia = models.CharField(
        max_length=15, choices=PREFERENCIA_CHOICES, default=PREFERENCIA_OMNIVORO,
        help_text="Se usa para recomendarte dietas compatibles con lo que comes."
    )

    PRESUPUESTO_ECONOMICO = 'economico'
    PRESUPUESTO_MODERADO = 'moderado'
    PRESUPUESTO_ALTO = 'alto'
    PRESUPUESTO_CHOICES = [
        (PRESUPUESTO_ECONOMICO, 'Económico'),
        (PRESUPUESTO_MODERADO, 'Moderado'),
        (PRESUPUESTO_ALTO, 'Sin restricción de presupuesto'),
    ]
    presupuesto_comida = models.CharField(
        max_length=10, choices=PRESUPUESTO_CHOICES, default=PRESUPUESTO_MODERADO,
        help_text="Cuánto puede/quiere gastar en su alimentación."
    )


    # --- Control del compromiso ---
    fecha_inicio_compromiso = models.DateField(
        default=timezone.now,
        help_text="Día 1 de su compromiso. Se usa para mostrar 'Día X de tu compromiso'."
    )

    def dias_de_compromiso(self):
        """Cuántos días han pasado desde que empezó (para el dashboard)."""
        return (timezone.now().date() - self.fecha_inicio_compromiso).days + 1

    def __str__(self):
        return self.nombre_para_mostrar or self.username
