from django.db import models


class Ejercicio(models.Model):
    """
    Un ejercicio de la biblioteca (ej. 'Cómo hacer una sentadilla').
    Se puede usar dentro de rutinas Y consultarse suelto en /rutinas/biblioteca/.
    """
    GRUPO_PIERNA = 'pierna'
    GRUPO_GLUTEO = 'gluteo'
    GRUPO_ESPALDA = 'espalda'
    GRUPO_PECHO = 'pecho'
    GRUPO_BRAZO = 'brazo'
    GRUPO_CORE = 'core'
    GRUPO_CUERPO_COMPLETO = 'cuerpo_completo'
    GRUPO_CHOICES = [
        (GRUPO_PIERNA, 'Pierna'),
        (GRUPO_GLUTEO, 'Glúteo'),
        (GRUPO_ESPALDA, 'Espalda'),
        (GRUPO_PECHO, 'Pecho'),
        (GRUPO_BRAZO, 'Brazo'),
        (GRUPO_CORE, 'Core / abdomen'),
        (GRUPO_CUERPO_COMPLETO, 'Cuerpo completo'),
    ]

    nombre = models.CharField(max_length=120)
    grupo_muscular = models.CharField(max_length=20, choices=GRUPO_CHOICES)
    descripcion_tecnica = models.TextField(
        help_text="Cómo se hace correctamente, en qué fijarse, errores comunes."
    )
    video_url = models.URLField(
        blank=True, help_text="Enlace a un video (YouTube, etc.) que muestre la técnica."
    )

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Rutina(models.Model):
    """
    Una rutina completa (ej. 'Casa - Sin equipo - 20 minutos - Principiante').
    Se filtra automáticamente según el perfil de cada usuaria.
    """
    CATEGORIA_FUERZA = 'fuerza'
    CATEGORIA_CARDIO = 'cardio'
    CATEGORIA_CHOICES = [
        (CATEGORIA_FUERZA, 'Fuerza'),
        (CATEGORIA_CARDIO, 'Cardio'),
    ]

    LUGAR_CASA = 'casa'
    LUGAR_GIMNASIO = 'gimnasio'
    LUGAR_CHOICES = [
        (LUGAR_CASA, 'En casa'),
        (LUGAR_GIMNASIO, 'En gimnasio'),
    ]

    NIVEL_PRINCIPIANTE = 'principiante'
    NIVEL_INTERMEDIO = 'intermedio'
    NIVEL_AVANZADO = 'avanzado'
    NIVEL_CHOICES = [
        (NIVEL_PRINCIPIANTE, 'Principiante'),
        (NIVEL_INTERMEDIO, 'Intermedio'),
        (NIVEL_AVANZADO, 'Avanzado'),
    ]

    EQUIPO_NINGUNO = 'ninguno'
    EQUIPO_MANCUERNAS = 'mancuernas'
    EQUIPO_BANDAS = 'bandas'
    EQUIPO_GIMNASIO_COMPLETO = 'gimnasio_completo'
    EQUIPO_CHOICES = [
        (EQUIPO_NINGUNO, 'Sin equipo'),
        (EQUIPO_MANCUERNAS, 'Mancuernas'),
        (EQUIPO_BANDAS, 'Bandas'),
        (EQUIPO_GIMNASIO_COMPLETO, 'Equipo de gimnasio'),
    ]

    TIPO_CARDIO_CAMINAR = 'caminar'
    TIPO_CARDIO_BICICLETA = 'bicicleta'
    TIPO_CARDIO_CORRER = 'correr'
    TIPO_CARDIO_HIIT = 'hiit'
    TIPO_CARDIO_CHOICES = [
        (TIPO_CARDIO_CAMINAR, 'Caminar'),
        (TIPO_CARDIO_BICICLETA, 'Bicicleta'),
        (TIPO_CARDIO_CORRER, 'Correr'),
        (TIPO_CARDIO_HIIT, 'HIIT'),
    ]

    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=10, choices=CATEGORIA_CHOICES, default=CATEGORIA_FUERZA)
    lugar = models.CharField(max_length=10, choices=LUGAR_CHOICES)
    nivel = models.CharField(max_length=15, choices=NIVEL_CHOICES)
    equipo = models.CharField(max_length=20, choices=EQUIPO_CHOICES, default=EQUIPO_NINGUNO)
    tipo_cardio = models.CharField(
        max_length=15, choices=TIPO_CARDIO_CHOICES, blank=True,
        help_text="Solo si la categoría es 'Cardio'."
    )
    minutos_duracion = models.PositiveSmallIntegerField(help_text="Duración aproximada en minutos.")
    descripcion = models.CharField(max_length=300, blank=True)

    ejercicios = models.ManyToManyField(Ejercicio, through='RutinaEjercicio')

    class Meta:
        ordering = ['lugar', 'nivel', 'minutos_duracion']

    def __str__(self):
        return self.nombre


class RutinaEjercicio(models.Model):
    """Un ejercicio dentro de una rutina, con sus series/repeticiones y orden."""
    rutina = models.ForeignKey(Rutina, on_delete=models.CASCADE, related_name='rutina_ejercicios')
    ejercicio = models.ForeignKey(Ejercicio, on_delete=models.CASCADE)
    orden = models.PositiveSmallIntegerField(default=1)
    series = models.PositiveSmallIntegerField(default=3)
    repeticiones = models.CharField(
        max_length=30, default='12',
        help_text="Ej. '12', '10-15', '30 segundos'."
    )
    descanso_segundos = models.PositiveSmallIntegerField(default=45)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.rutina} - {self.ejercicio}"
