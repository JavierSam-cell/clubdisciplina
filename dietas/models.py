from django.db import models


class Comida(models.Model):
    """
    Un platillo/comida de la biblioteca (ej. 'Avena con fruta').
    Se usa dentro de dietas, como los ejercicios dentro de las rutinas.
    """
    MOMENTO_DESAYUNO = 'desayuno'
    MOMENTO_COLACION_AM = 'colacion_am'
    MOMENTO_COMIDA = 'comida'
    MOMENTO_COLACION_PM = 'colacion_pm'
    MOMENTO_CENA = 'cena'
    MOMENTO_CHOICES = [
        (MOMENTO_DESAYUNO, 'Desayuno'),
        (MOMENTO_COLACION_AM, 'Colación (mañana)'),
        (MOMENTO_COMIDA, 'Comida'),
        (MOMENTO_COLACION_PM, 'Colación (tarde)'),
        (MOMENTO_CENA, 'Cena'),
    ]

    nombre = models.CharField(max_length=120)
    momento_sugerido = models.CharField(max_length=15, choices=MOMENTO_CHOICES)
    ingredientes = models.TextField(help_text="Un ingrediente por línea, con cantidades.")
    preparacion = models.TextField(blank=True, help_text="Pasos rápidos de preparación.")
    calorias_aprox = models.PositiveSmallIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class Dieta(models.Model):
    """
    Un plan de alimentación completo (ej. 'Económica - Bajar de peso - 3 comidas').
    Se filtra automáticamente según el perfil de cada usuaria, igual que las rutinas.
    """
    CATEGORIA_ECONOMICA = 'economica'
    CATEGORIA_VEGETARIANA = 'vegetariana'
    CATEGORIA_VEGANA = 'vegana'
    CATEGORIA_MEXICANA = 'mexicana'
    CATEGORIA_MEAL_PREP = 'meal_prep'
    CATEGORIA_ALTA_PROTEINA = 'alta_proteina'
    CATEGORIA_BAJA_CARBOHIDRATOS = 'baja_carbohidratos'
    CATEGORIA_SIN_GLUTEN = 'sin_gluten'
    CATEGORIA_RAPIDA = 'rapida'
    CATEGORIA_TRADICIONAL = 'tradicional'
    CATEGORIA_CHOICES = [
        (CATEGORIA_ECONOMICA, 'Económica'),
        (CATEGORIA_VEGETARIANA, 'Vegetariana'),
        (CATEGORIA_VEGANA, 'Vegana'),
        (CATEGORIA_MEXICANA, 'Mexicana'),
        (CATEGORIA_MEAL_PREP, 'Meal prep / domingo'),
        (CATEGORIA_ALTA_PROTEINA, 'Alta en proteína'),
        (CATEGORIA_BAJA_CARBOHIDRATOS, 'Baja en carbohidratos'),
        (CATEGORIA_SIN_GLUTEN, 'Sin gluten'),
        (CATEGORIA_RAPIDA, 'Rápida / poco tiempo'),
        (CATEGORIA_TRADICIONAL, 'Tradicional / casera'),
    ]

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

    PRESUPUESTO_ECONOMICO = 'economico'
    PRESUPUESTO_MODERADO = 'moderado'
    PRESUPUESTO_ALTO = 'alto'
    PRESUPUESTO_CHOICES = [
        (PRESUPUESTO_ECONOMICO, 'Económico'),
        (PRESUPUESTO_MODERADO, 'Moderado'),
        (PRESUPUESTO_ALTO, 'Sin restricción de presupuesto'),
    ]

    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=20, choices=CATEGORIA_CHOICES)
    objetivo = models.CharField(max_length=20, choices=OBJETIVO_CHOICES, default=OBJETIVO_SALUD)
    preferencia = models.CharField(max_length=15, choices=PREFERENCIA_CHOICES, default=PREFERENCIA_OMNIVORO)
    presupuesto = models.CharField(max_length=10, choices=PRESUPUESTO_CHOICES, default=PRESUPUESTO_MODERADO)
    comidas_por_dia = models.PositiveSmallIntegerField(default=4)
    calorias_aproximadas = models.PositiveSmallIntegerField(
        null=True, blank=True, help_text="Calorías aproximadas por día."
    )
    descripcion = models.CharField(max_length=300, blank=True)

    comidas = models.ManyToManyField(Comida, through='DietaComida')

    class Meta:
        ordering = ['categoria', 'objetivo']
        verbose_name_plural = 'dietas'

    def __str__(self):
        return self.nombre


class DietaComida(models.Model):
    """Una comida dentro de una dieta, con su momento del día y orden (menú de un día tipo)."""
    dieta = models.ForeignKey(Dieta, on_delete=models.CASCADE, related_name='dieta_comidas')
    comida = models.ForeignKey(Comida, on_delete=models.CASCADE)
    orden = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.dieta} - {self.comida}"
