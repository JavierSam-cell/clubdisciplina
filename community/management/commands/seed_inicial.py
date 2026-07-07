from django.core.management.base import BaseCommand

from community.models import Frase, OpcionRetoBiblioteca
from community.utils import generar_semana_de_retos
from tracking.models import Medalla
from rutinas.models import Ejercicio, Rutina, RutinaEjercicio
from dietas.models import Comida, Dieta, DietaComida


FRASES_INICIALES = [
    # (texto, momento)
    ("Hoy nadie va a entrenar por ti.", Frase.MOMENTO_GENERAL),
    ("Tu cuerpo refleja tus hábitos, no tus intenciones.", Frase.MOMENTO_GENERAL),
    ("La disciplina siempre vence al talento.", Frase.MOMENTO_GENERAL),

    ("Hoy es el día 1. No el lunes, no el próximo mes: hoy.", Frase.MOMENTO_DIA_1),
    ("No necesitas la dieta perfecta. Necesitas empezar.", Frase.MOMENTO_DIA_1),
    ("Nadie llega a la meta sin dar el primer paso incómodo.", Frase.MOMENTO_DIA_1),

    ("Llevas días demostrándote que sí puedes. Sigue.", Frase.MOMENTO_RACHA_ACTIVA),
    ("Esta racha no es suerte, es disciplina acumulada.", Frase.MOMENTO_RACHA_ACTIVA),
    ("Cada día que sigues, se vuelve más parte de quién eres.", Frase.MOMENTO_RACHA_ACTIVA),

    ("No dejes que una mala tarde se convierta en una mala semana. Hoy puedes continuar.", Frase.MOMENTO_RACHA_ROTA),
    ("Un día perdido no borra los que ya ganaste. Retómalo hoy.", Frase.MOMENTO_RACHA_ROTA),
    ("Lo que importa no es que ayer fallaste, es qué haces hoy con eso.", Frase.MOMENTO_RACHA_ROTA),

    ("El peso se puede estancar. El hábito, si lo sostienes, no.", Frase.MOMENTO_ESTANCAMIENTO),
    ("Los resultados a veces se esconden unas semanas antes de mostrarse.", Frase.MOMENTO_ESTANCAMIENTO),

    ("Planea tu semana antes de que la semana te planee a ti.", Frase.MOMENTO_DOMINGO),
    ("Este domingo, decide qué tipo de semana quieres tener.", Frase.MOMENTO_DOMINGO),
]

OPCIONES_RETO_INICIALES = [
    # (categoria, texto, puntos)
    (OpcionRetoBiblioteca.CATEGORIA_AGUA, "Toma 2 litros de agua al día toda la semana", 20),
    (OpcionRetoBiblioteca.CATEGORIA_AGUA, "Toma 2.5 litros de agua al día toda la semana", 25),
    (OpcionRetoBiblioteca.CATEGORIA_AGUA, "Toma 8 vasos de agua diarios toda la semana", 20),

    (OpcionRetoBiblioteca.CATEGORIA_ENTRENAMIENTO, "Entrena 3 días esta semana", 30),
    (OpcionRetoBiblioteca.CATEGORIA_ENTRENAMIENTO, "Entrena 4 días esta semana", 40),
    (OpcionRetoBiblioteca.CATEGORIA_ENTRENAMIENTO, "Haz 5 entrenamientos esta semana", 50),
    (OpcionRetoBiblioteca.CATEGORIA_ENTRENAMIENTO, "Haz 3 entrenamientos de pierna esta semana", 35),

    (OpcionRetoBiblioteca.CATEGORIA_ALIMENTACION, "Pasa la semana sin refrescos", 30),
    (OpcionRetoBiblioteca.CATEGORIA_ALIMENTACION, "Come fruta todos los días de la semana", 25),
    (OpcionRetoBiblioteca.CATEGORIA_ALIMENTACION, "Desayuna todos los días de la semana", 25),
    (OpcionRetoBiblioteca.CATEGORIA_ALIMENTACION, "Incluye proteína en cada comida esta semana", 30),

    (OpcionRetoBiblioteca.CATEGORIA_MENTAL, "Duerme antes de las 11pm tres noches esta semana", 10),
    (OpcionRetoBiblioteca.CATEGORIA_MENTAL, "Camina 10 minutos diarios toda la semana", 10),
    (OpcionRetoBiblioteca.CATEGORIA_MENTAL, "Lee 15 minutos diarios toda la semana", 10),
    (OpcionRetoBiblioteca.CATEGORIA_MENTAL, "Medita 5 minutos diarios toda la semana", 10),

    (OpcionRetoBiblioteca.CATEGORIA_FOTO_PROGRESO, "Súbete una foto de progreso esta semana", 20),
]

MEDALLAS_INICIALES = [
    ("Primera semana", "7 días seguidos entrenando.", "🥉", Medalla.TIPO_RACHA_DIAS, 7),
    ("Un mes de disciplina", "30 días seguidos entrenando.", "🥈", Medalla.TIPO_RACHA_DIAS, 30),
    ("Dos meses sin excusas", "60 días seguidos entrenando.", "🥇", Medalla.TIPO_RACHA_DIAS, 60),
    ("100 días de compromiso", "100 días seguidos entrenando.", "🏆", Medalla.TIPO_RACHA_DIAS, 100),
    ("Primeros 10 entrenamientos", "10 entrenamientos acumulados en total.", "💪", Medalla.TIPO_TOTAL_ENTRENAMIENTOS, 10),
    ("100 entrenamientos", "100 entrenamientos acumulados en total.", "🎖️", Medalla.TIPO_TOTAL_ENTRENAMIENTOS, 100),
]


class Command(BaseCommand):
    help = "Crea frases del sistema, medallas y un reto semanal de ejemplo para no arrancar con la app vacía."

    def handle(self, *args, **options):
        creadas = 0
        for texto, momento in FRASES_INICIALES:
            _, creada = Frase.objects.get_or_create(
                texto=texto, defaults={'origen': Frase.ORIGEN_SISTEMA, 'momento': momento, 'aprobado': True}
            )
            creadas += int(creada)
        self.stdout.write(self.style.SUCCESS(f"Frases del sistema creadas: {creadas}"))

        creadas = 0
        for nombre, desc, icono, tipo, valor in MEDALLAS_INICIALES:
            _, creada = Medalla.objects.get_or_create(
                nombre=nombre,
                defaults={'descripcion': desc, 'icono': icono, 'tipo_condicion': tipo, 'valor_condicion': valor}
            )
            creadas += int(creada)
        self.stdout.write(self.style.SUCCESS(f"Medallas creadas: {creadas}"))

        creadas = 0
        for categoria, texto, puntos in OPCIONES_RETO_INICIALES:
            _, creada = OpcionRetoBiblioteca.objects.get_or_create(
                texto=texto, defaults={'categoria': categoria, 'puntos': puntos}
            )
            creadas += int(creada)
        self.stdout.write(self.style.SUCCESS(f"Opciones de la biblioteca de retos creadas: {creadas}"))

        semana = generar_semana_de_retos()
        self.stdout.write(self.style.SUCCESS(
            f"Semana de retos generada: {semana.fecha_inicio} – {semana.fecha_fin}"
        ))

        # --- Ejercicios de la biblioteca ---
        ejercicios_data = [
            ("Sentadilla", Ejercicio.GRUPO_PIERNA,
             "Pies al ancho de hombros, baja como si te sentaras en una silla, "
             "rodillas alineadas con los pies, espalda recta.", ""),
            ("Zancada / desplante", Ejercicio.GRUPO_PIERNA,
             "Da un paso al frente, baja la rodilla trasera casi al piso, "
             "mantén el torso recto.", ""),
            ("Puente de glúteo", Ejercicio.GRUPO_GLUTEO,
             "Acostada boca arriba, rodillas flexionadas, empuja la cadera hacia arriba "
             "apretando el glúteo.", ""),
            ("Plancha (plank)", Ejercicio.GRUPO_CORE,
             "Apoyo en antebrazos y puntas de pie, cuerpo en línea recta, "
             "abdomen contraído.", ""),
            ("Flexión de pecho (push-up)", Ejercicio.GRUPO_PECHO,
             "Manos un poco más anchas que los hombros, baja controlando el torso, "
             "puedes apoyar rodillas si es necesario.", ""),
            ("Remo con banda o mancuerna", Ejercicio.GRUPO_ESPALDA,
             "Jala hacia tu abdomen apretando los omóplatos, controla el regreso.", ""),
            ("Curl de bíceps", Ejercicio.GRUPO_BRAZO,
             "Codos pegados al cuerpo, sube el peso sin balancear la espalda.", ""),
            ("Burpee", Ejercicio.GRUPO_CUERPO_COMPLETO,
             "De pie a plancha a salto; ideal para HIIT, ajusta el ritmo a tu nivel.", ""),
        ]
        ejercicios = {}
        creados = 0
        for nombre, grupo, desc, video in ejercicios_data:
            obj, creado = Ejercicio.objects.get_or_create(
                nombre=nombre,
                defaults={'grupo_muscular': grupo, 'descripcion_tecnica': desc, 'video_url': video}
            )
            ejercicios[nombre] = obj
            creados += int(creado)
        self.stdout.write(self.style.SUCCESS(f"Ejercicios creados: {creados}"))

        # --- Rutinas de ejemplo ---
        rutinas_data = [
            {
                'nombre': 'Casa - Sin equipo - 20 min - Principiante',
                'categoria': Rutina.CATEGORIA_FUERZA,
                'lugar': Rutina.LUGAR_CASA,
                'nivel': Rutina.NIVEL_PRINCIPIANTE,
                'equipo': Rutina.EQUIPO_NINGUNO,
                'minutos_duracion': 20,
                'descripcion': 'Rutina de cuerpo completo para empezar, sin necesidad de equipo.',
                'ejercicios': [
                    ('Sentadilla', 3, '12', 45),
                    ('Puente de glúteo', 3, '15', 30),
                    ('Plancha (plank)', 3, '20 segundos', 30),
                    ('Flexión de pecho (push-up)', 3, '8-10', 45),
                ],
            },
            {
                'nombre': 'Casa - Sin equipo - 30 min - Intermedio',
                'categoria': Rutina.CATEGORIA_FUERZA,
                'lugar': Rutina.LUGAR_CASA,
                'nivel': Rutina.NIVEL_INTERMEDIO,
                'equipo': Rutina.EQUIPO_NINGUNO,
                'minutos_duracion': 30,
                'descripcion': 'Un poco más de volumen e intensidad que la rutina de principiante.',
                'ejercicios': [
                    ('Sentadilla', 4, '15', 40),
                    ('Zancada / desplante', 3, '12 por pierna', 40),
                    ('Flexión de pecho (push-up)', 4, '12', 40),
                    ('Plancha (plank)', 3, '40 segundos', 30),
                    ('Burpee', 3, '10', 45),
                ],
            },
            {
                'nombre': 'Gimnasio - 45 min - Principiante',
                'categoria': Rutina.CATEGORIA_FUERZA,
                'lugar': Rutina.LUGAR_GIMNASIO,
                'nivel': Rutina.NIVEL_PRINCIPIANTE,
                'equipo': Rutina.EQUIPO_GIMNASIO_COMPLETO,
                'minutos_duracion': 45,
                'descripcion': 'Introducción a máquinas y pesas libres básicas.',
                'ejercicios': [
                    ('Sentadilla', 3, '12', 60),
                    ('Remo con banda o mancuerna', 3, '12', 45),
                    ('Curl de bíceps', 3, '12', 45),
                    ('Plancha (plank)', 3, '30 segundos', 30),
                ],
            },
            {
                'nombre': 'HIIT - 20 min',
                'categoria': Rutina.CATEGORIA_CARDIO,
                'lugar': Rutina.LUGAR_CASA,
                'nivel': Rutina.NIVEL_INTERMEDIO,
                'equipo': Rutina.EQUIPO_NINGUNO,
                'tipo_cardio': Rutina.TIPO_CARDIO_HIIT,
                'minutos_duracion': 20,
                'descripcion': 'Intervalos de alta intensidad para maximizar el tiempo.',
                'ejercicios': [
                    ('Burpee', 4, '30 segundos', 30),
                    ('Sentadilla', 4, '30 segundos', 30),
                    ('Plancha (plank)', 4, '30 segundos', 30),
                ],
            },
        ]

        rutinas_creadas = 0
        for data in rutinas_data:
            ejercicios_rutina = data.pop('ejercicios')
            rutina, creada = Rutina.objects.get_or_create(
                nombre=data['nombre'], defaults=data
            )
            rutinas_creadas += int(creada)
            if creada:
                for i, (nombre_ej, series, reps, descanso) in enumerate(ejercicios_rutina, start=1):
                    RutinaEjercicio.objects.create(
                        rutina=rutina, ejercicio=ejercicios[nombre_ej],
                        orden=i, series=series, repeticiones=reps, descanso_segundos=descanso,
                    )
        self.stdout.write(self.style.SUCCESS(f"Rutinas creadas: {rutinas_creadas}"))

        # --- Comidas de la biblioteca ---
        comidas_data = [
            ("Avena con fruta y semillas", Comida.MOMENTO_DESAYUNO,
             "1/2 taza de avena\n1 taza de leche o bebida vegetal\n1 platano o fruta de temporada\n1 cda de semillas (chia o linaza)",
             "Cocina la avena con la leche, agrega la fruta picada y las semillas al servir.", 320),
            ("Huevos con nopales y frijoles", Comida.MOMENTO_DESAYUNO,
             "2 huevos\n1 taza de nopales asados\n1/2 taza de frijoles\n2 tortillas de maiz",
             "Revuelve los huevos, sirve con nopales y frijoles calientes.", 380),
            ("Yogur con granola y fruta", Comida.MOMENTO_COLACION_AM,
             "1 yogur natural\n2 cdas de granola\n1/2 taza de fruta picada",
             "Mezcla todo en un tazon.", 210),
            ("Punado de nueces o cacahuates", Comida.MOMENTO_COLACION_AM,
             "1 punado (30g) de nueces, almendras o cacahuates naturales",
             "Listo para comer, sin necesidad de preparacion.", 180),
            ("Pechuga de pollo con verduras y arroz", Comida.MOMENTO_COMIDA,
             "150g de pechuga de pollo\n1 taza de verduras al vapor\n1/2 taza de arroz integral",
             "Cocina el pollo a la plancha, acompana con verduras y arroz.", 480),
            ("Lentejas con verduras", Comida.MOMENTO_COMIDA,
             "1 taza de lentejas cocidas\n1/2 taza de verduras salteadas\n1 tortilla de maiz",
             "Guisa las lentejas con las verduras, sirve caliente.", 400),
            ("Tacos de frijol con nopales", Comida.MOMENTO_COMIDA,
             "1 taza de frijoles refritos\n1 taza de nopales\n3 tortillas de maiz\nSalsa al gusto",
             "Calienta los frijoles, arma los tacos con nopales y salsa.", 420),
            ("Fruta picada con limon y chile", Comida.MOMENTO_COLACION_PM,
             "1 taza de fruta picada (jicama, pepino, mango)\nLimon y chile piquin al gusto",
             "Mezcla la fruta con limon y chile.", 90),
            ("Pescado a la plancha con ensalada", Comida.MOMENTO_CENA,
             "150g de filete de pescado\n2 tazas de ensalada verde\n1 cda de aceite de oliva",
             "Cocina el pescado a la plancha, acompana con la ensalada aderezada.", 350),
            ("Quesadillas de champinones", Comida.MOMENTO_CENA,
             "2 tortillas de maiz\n1 taza de champinones salteados\n30g de queso",
             "Rellena las tortillas y cocina en comal hasta gratinar.", 340),
            ("Ensalada de garbanzo", Comida.MOMENTO_CENA,
             "1 taza de garbanzo cocido\n1 taza de verduras picadas\n1 cda de aceite de oliva y limon",
             "Mezcla todos los ingredientes en un tazon.", 310),
            ("Sopa de verduras con tofu", Comida.MOMENTO_CENA,
             "2 tazas de caldo de verduras\n100g de tofu en cubos\nVerduras al gusto",
             "Hierve el caldo con las verduras y el tofu 10 minutos.", 260),
        ]
        comidas = {}
        creadas = 0
        for nombre, momento, ingredientes, prep, kcal in comidas_data:
            obj, creada = Comida.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'momento_sugerido': momento, 'ingredientes': ingredientes,
                    'preparacion': prep, 'calorias_aprox': kcal,
                }
            )
            comidas[nombre] = obj
            creadas += int(creada)
        self.stdout.write(self.style.SUCCESS(f"Comidas creadas: {creadas}"))

        # --- Las 10 dietas, una por categoria (mismo patron que las rutinas) ---
        dietas_data = [
            {
                'nombre': 'Economica - Bajar de peso',
                'categoria': Dieta.CATEGORIA_ECONOMICA,
                'objetivo': Dieta.OBJETIVO_BAJAR_PESO,
                'preferencia': Dieta.PREFERENCIA_OMNIVORO,
                'presupuesto': Dieta.PRESUPUESTO_ECONOMICO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1500,
                'descripcion': 'Ingredientes accesibles de temporada, sin sacrificar nutricion.',
                'menu': ['Huevos con nopales y frijoles', 'Punado de nueces o cacahuates',
                         'Tacos de frijol con nopales', 'Sopa de verduras con tofu'],
            },
            {
                'nombre': 'Vegetariana - Salud general',
                'categoria': Dieta.CATEGORIA_VEGETARIANA,
                'objetivo': Dieta.OBJETIVO_SALUD,
                'preferencia': Dieta.PREFERENCIA_VEGETARIANA,
                'presupuesto': Dieta.PRESUPUESTO_MODERADO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1700,
                'descripcion': 'Sin carne, con buenas fuentes de proteina vegetal.',
                'menu': ['Avena con fruta y semillas', 'Yogur con granola y fruta',
                         'Lentejas con verduras', 'Ensalada de garbanzo'],
            },
            {
                'nombre': 'Vegana - Tonificar',
                'categoria': Dieta.CATEGORIA_VEGANA,
                'objetivo': Dieta.OBJETIVO_TONIFICAR,
                'preferencia': Dieta.PREFERENCIA_VEGANA,
                'presupuesto': Dieta.PRESUPUESTO_MODERADO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1600,
                'descripcion': 'Cero productos de origen animal, alta en fibra y legumbres.',
                'menu': ['Avena con fruta y semillas', 'Fruta picada con limon y chile',
                         'Ensalada de garbanzo', 'Sopa de verduras con tofu'],
            },
            {
                'nombre': 'Mexicana - Salud general',
                'categoria': Dieta.CATEGORIA_MEXICANA,
                'objetivo': Dieta.OBJETIVO_SALUD,
                'preferencia': Dieta.PREFERENCIA_OMNIVORO,
                'presupuesto': Dieta.PRESUPUESTO_MODERADO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1800,
                'descripcion': 'Platillos tradicionales mexicanos, balanceados en porciones.',
                'menu': ['Huevos con nopales y frijoles', 'Fruta picada con limon y chile',
                         'Tacos de frijol con nopales', 'Quesadillas de champinones'],
            },
            {
                'nombre': 'Meal prep - Bajar de peso',
                'categoria': Dieta.CATEGORIA_MEAL_PREP,
                'objetivo': Dieta.OBJETIVO_BAJAR_PESO,
                'preferencia': Dieta.PREFERENCIA_OMNIVORO,
                'presupuesto': Dieta.PRESUPUESTO_MODERADO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1550,
                'descripcion': 'Pensada para preparar el domingo y tener lista toda la semana.',
                'menu': ['Avena con fruta y semillas', 'Punado de nueces o cacahuates',
                         'Pechuga de pollo con verduras y arroz', 'Pescado a la plancha con ensalada'],
            },
            {
                'nombre': 'Alta en proteina - Ganar musculo',
                'categoria': Dieta.CATEGORIA_ALTA_PROTEINA,
                'objetivo': Dieta.OBJETIVO_GANAR_MUSCULO,
                'preferencia': Dieta.PREFERENCIA_OMNIVORO,
                'presupuesto': Dieta.PRESUPUESTO_ALTO,
                'comidas_por_dia': 5,
                'calorias_aproximadas': 2200,
                'descripcion': 'Mas proteina en cada comida para apoyar el desarrollo muscular.',
                'menu': ['Huevos con nopales y frijoles', 'Yogur con granola y fruta',
                         'Pechuga de pollo con verduras y arroz', 'Punado de nueces o cacahuates',
                         'Pescado a la plancha con ensalada'],
            },
            {
                'nombre': 'Baja en carbohidratos - Bajar de peso',
                'categoria': Dieta.CATEGORIA_BAJA_CARBOHIDRATOS,
                'objetivo': Dieta.OBJETIVO_BAJAR_PESO,
                'preferencia': Dieta.PREFERENCIA_OMNIVORO,
                'presupuesto': Dieta.PRESUPUESTO_MODERADO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1450,
                'descripcion': 'Menos cereales y azucares, mas verduras y proteina.',
                'menu': ['Huevos con nopales y frijoles', 'Fruta picada con limon y chile',
                         'Pescado a la plancha con ensalada', 'Sopa de verduras con tofu'],
            },
            {
                'nombre': 'Sin gluten - Salud general',
                'categoria': Dieta.CATEGORIA_SIN_GLUTEN,
                'objetivo': Dieta.OBJETIVO_SALUD,
                'preferencia': Dieta.PREFERENCIA_SIN_GLUTEN,
                'presupuesto': Dieta.PRESUPUESTO_MODERADO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1700,
                'descripcion': 'Sin trigo ni derivados; basada en maiz, arroz y proteinas naturales.',
                'menu': ['Huevos con nopales y frijoles', 'Fruta picada con limon y chile',
                         'Pechuga de pollo con verduras y arroz', 'Ensalada de garbanzo'],
            },
            {
                'nombre': 'Rapida - Poco tiempo para cocinar',
                'categoria': Dieta.CATEGORIA_RAPIDA,
                'objetivo': Dieta.OBJETIVO_SALUD,
                'preferencia': Dieta.PREFERENCIA_OMNIVORO,
                'presupuesto': Dieta.PRESUPUESTO_MODERADO,
                'comidas_por_dia': 3,
                'calorias_aproximadas': 1600,
                'descripcion': 'Comidas con pocos pasos e ingredientes, ideal para dias sin tiempo.',
                'menu': ['Yogur con granola y fruta', 'Quesadillas de champinones',
                         'Punado de nueces o cacahuates'],
            },
            {
                'nombre': 'Tradicional / casera - Salud general',
                'categoria': Dieta.CATEGORIA_TRADICIONAL,
                'objetivo': Dieta.OBJETIVO_SALUD,
                'preferencia': Dieta.PREFERENCIA_OMNIVORO,
                'presupuesto': Dieta.PRESUPUESTO_ECONOMICO,
                'comidas_por_dia': 4,
                'calorias_aproximadas': 1750,
                'descripcion': 'Guisos de siempre, como los de casa, en porciones cuidadas.',
                'menu': ['Avena con fruta y semillas', 'Fruta picada con limon y chile',
                         'Lentejas con verduras', 'Quesadillas de champinones'],
            },
        ]

        dietas_creadas = 0
        for data in dietas_data:
            menu = data.pop('menu')
            dieta, creada = Dieta.objects.get_or_create(
                nombre=data['nombre'], defaults=data
            )
            dietas_creadas += int(creada)
            if creada:
                for i, nombre_comida in enumerate(menu, start=1):
                    DietaComida.objects.create(
                        dieta=dieta, comida=comidas[nombre_comida], orden=i,
                    )
        self.stdout.write(self.style.SUCCESS(f"Dietas creadas: {dietas_creadas}"))

        self.stdout.write(self.style.SUCCESS("Listo. La app ya tiene contenido inicial."))
