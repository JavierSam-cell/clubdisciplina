import random
from datetime import timedelta
from django.db import models, IntegrityError
from django.db.models import Q
from django.utils import timezone
from .models import (
    Frase, CompaneraDeCompromiso,
    OpcionRetoBiblioteca, RetoSemanal, ItemRetoSemanal,
    ParticipacionItemReto, PuntosEvento,
)
from tracking.utils import calcular_racha_actual
from tracking.models import RegistroDiario, Medalla, MedallaObtenida


def _hubo_racha_rota_ayer(usuario):
    """
    ¿Ayer la usuaria no entrenó, después de tener una racha activa?
    Este es el momento más delicado: aquí es donde se gana o se pierde
    a la usuaria, así que la frase debe ser de reenganche, no de regaño.
    """
    ayer = timezone.now().date() - timedelta(days=1)
    registro_ayer = RegistroDiario.objects.filter(usuario=usuario, fecha=ayer).first()
    if registro_ayer is None or registro_ayer.entreno:
        return False
    # Hubo un registro de "no entrenó" ayer: consideramos que es momento de reenganche
    # si además traía algo de racha antes de eso (evita marcarlo desde el día 1).
    return True


def determinar_momento(usuario, fecha=None):
    """Decide qué categoría de frase le corresponde a la usuaria en `fecha` (hoy por defecto)."""
    fecha = fecha or timezone.now().date()
    dias_compromiso = usuario.dias_de_compromiso()
    racha = calcular_racha_actual(usuario)

    if _hubo_racha_rota_ayer(usuario):
        return Frase.MOMENTO_RACHA_ROTA
    if dias_compromiso <= 3:
        return Frase.MOMENTO_DIA_1
    if racha >= 7:
        return Frase.MOMENTO_RACHA_ACTIVA
    if fecha.weekday() == 6:  # domingo
        return Frase.MOMENTO_DOMINGO
    return Frase.MOMENTO_GENERAL


def frase_para_usuario(usuario, fecha=None):
    """
    Regresa la frase del día para el momento actual de la usuaria.

    A diferencia de una elección aleatoria en cada request, aquí la frase
    se elige con el número de día del año (`tm_yday`) módulo el total de
    frases candidatas para ese momento. Esto hace que:
      - Todas las veces que la usuaria entre el mismo día vea la misma frase.
      - Al día siguiente, el índice cambie y por lo tanto la frase también
        (salvo coincidencia si hay muy pocas frases cargadas).
    No requiere guardar nada en base de datos ni tocar el modelo Frase.
    """
    fecha = fecha or timezone.now().date()
    momento = determinar_momento(usuario, fecha)

    candidatas = list(Frase.objects.aprobados().filter(momento=momento).order_by('id'))
    if not candidatas:
        candidatas = list(Frase.objects.aprobados().filter(momento=Frase.MOMENTO_GENERAL).order_by('id'))

    if not candidatas:
        return None

    indice = fecha.timetuple().tm_yday % len(candidatas)
    return candidatas[indice]


# --- Mensaje motivacional fijo por día de la semana (independiente de la frase) ---

MENSAJES_POR_DIA_SEMANA = {
    0: "💪 Empieza fuerte la semana.",
    1: "🔥 No rompas la racha.",
    2: "🚀 Ya llegaste a la mitad.",
    3: "⭐ La constancia gana.",
    4: "🎉 Termina la semana con orgullo.",
    5: "🏋️ Hoy también cuenta.",
    6: "📈 Planea la próxima semana.",
}


def mensaje_motivacional_dia(fecha=None):
    """Mensaje corto y fijo según el día de la semana (0=lunes ... 6=domingo)."""
    fecha = fecha or timezone.now().date()
    return MENSAJES_POR_DIA_SEMANA[fecha.weekday()]


# --- Retos semanales: biblioteca por categoría + generación automática ---

def reto_semanal_activo():
    """
    El RetoSemanal (semana de retos) vigente hoy. Si todavía no existe
    (por ejemplo, es la primera vez que alguien entra esta semana), se
    genera aquí mismo automáticamente — no depende de que un cron o una
    tarea programada corra en el servidor.
    """
    hoy = timezone.now().date()
    reto = RetoSemanal.objects.filter(fecha_inicio__lte=hoy, fecha_fin__gte=hoy).first()
    if reto is None:
        reto = generar_semana_de_retos()
    return reto


def generar_semana_de_retos(fecha_inicio=None, semanas_evitar_repeticion=4):
    """
    Genera (o regresa, si ya existe) la semana de retos que arranca en
    `fecha_inicio` (el lunes de esa semana por defecto). Por cada categoría
    activa en la biblioteca, elige una opción al azar, evitando repetir -en
    la medida de lo posible- las opciones usadas en las últimas
    `semanas_evitar_repeticion` semanas, para que no se sienta igual cada
    lunes.
    """
    hoy = timezone.now().date()
    fecha_inicio = fecha_inicio or (hoy - timedelta(days=hoy.weekday()))  # lunes de esta semana
    fecha_fin = fecha_inicio + timedelta(days=6)

    existente = RetoSemanal.objects.filter(fecha_inicio=fecha_inicio).first()
    if existente:
        return existente

    try:
        semana = RetoSemanal.objects.create(
            fecha_inicio=fecha_inicio, fecha_fin=fecha_fin, generado_automaticamente=True
        )
    except IntegrityError:
        # Otra request generó la semana en el mismo instante: usamos esa.
        return RetoSemanal.objects.get(fecha_inicio=fecha_inicio)

    limite_historial = fecha_inicio - timedelta(days=7 * semanas_evitar_repeticion)
    opciones_recientes_ids = set(
        ItemRetoSemanal.objects.filter(
            reto_semanal__fecha_inicio__gte=limite_historial,
            reto_semanal__fecha_inicio__lt=fecha_inicio,
        ).values_list('opcion_id', flat=True)
    )

    for categoria, _ in OpcionRetoBiblioteca.CATEGORIA_CHOICES:
        candidatas = list(OpcionRetoBiblioteca.objects.filter(categoria=categoria, activo=True))
        if not candidatas:
            continue  # esa categoría no tiene nada en la biblioteca todavía

        sin_repetir = [c for c in candidatas if c.id not in opciones_recientes_ids]
        elegida = random.choice(sin_repetir or candidatas)

        ItemRetoSemanal.objects.create(
            reto_semanal=semana,
            categoria=categoria,
            opcion=elegida,
            texto=elegida.texto,
            puntos=elegida.puntos,
        )

    return semana


# --- Puntos: ledger simple + bono por racha ---

def total_puntos(usuario):
    """Puntos acumulados históricos de la usuaria (suma de todo el ledger)."""
    resultado = PuntosEvento.objects.filter(usuario=usuario).aggregate(total=models.Sum('puntos'))
    return resultado['total'] or 0


def registrar_puntos(usuario, puntos, motivo, detalle=''):
    return PuntosEvento.objects.create(usuario=usuario, puntos=puntos, motivo=motivo, detalle=detalle)


def marcar_item_reto_completado(usuario, item):
    """Marca un ítem del reto como completado y otorga sus puntos (una sola vez)."""
    participacion, creada = ParticipacionItemReto.objects.get_or_create(item=item, usuario=usuario)
    if participacion.completado:
        return participacion  # ya estaba completado, no se vuelven a dar puntos

    participacion.completado = True
    participacion.fecha_completado = timezone.now()
    participacion.save()

    registrar_puntos(usuario, item.puntos, PuntosEvento.MOTIVO_RETO, detalle=item.texto)
    return participacion


# Bono de puntos exactamente el día en que la racha llega a estos umbrales.
# (7/30/60/100 además coinciden con las medallas por racha ya sembradas en
# tracking.Medalla; 3 y 15 son solo puntos, sin medalla asociada.)
PUNTOS_BONO_RACHA = {3: 10, 7: 30, 15: 60, 30: 100, 100: 300}


def evaluar_bono_racha(usuario, racha_actual):
    """
    Se llama justo después de guardar el check-in del día. Si la racha
    recién llegó exactamente a uno de los umbrales, otorga el bono de
    puntos correspondiente (una sola vez por umbral, gracias a que el
    check-in ya es único por usuaria/día) y, si aplica, la medalla.
    """
    puntos_umbral = PUNTOS_BONO_RACHA.get(racha_actual)
    if puntos_umbral:
        registrar_puntos(
            usuario, puntos_umbral, PuntosEvento.MOTIVO_RACHA,
            detalle=f"Racha de {racha_actual} días"
        )

    for medalla in Medalla.objects.filter(
        tipo_condicion=Medalla.TIPO_RACHA_DIAS, valor_condicion=racha_actual
    ):
        MedallaObtenida.objects.get_or_create(usuario=usuario, medalla=medalla)


# --- Compañera de compromiso: emparejamiento automático ---

def pareja_activa_de(usuario):
    """Devuelve la pareja activa de esta usuaria (como usuario_1 o usuario_2), o None."""
    return CompaneraDeCompromiso.objects.filter(
        Q(usuario_1=usuario) | Q(usuario_2=usuario), activa=True
    ).first()


def usuarias_sin_pareja(excluir=None):
    """Usuarias que ahora mismo no tienen ninguna pareja activa."""
    from django.contrib.auth import get_user_model
    Usuario = get_user_model()

    emparejadas_ids = set(
        CompaneraDeCompromiso.objects.filter(activa=True).values_list('usuario_1_id', flat=True)
    ) | set(
        CompaneraDeCompromiso.objects.filter(activa=True).values_list('usuario_2_id', flat=True)
    )
    qs = Usuario.objects.exclude(id__in=emparejadas_ids)
    if excluir is not None:
        qs = qs.exclude(id=excluir.id)
    return qs


def buscar_companera_compatible(usuario):
    """
    Busca la mejor candidata disponible para emparejar con `usuario`, en orden de prioridad:
      1) mismo horario de entreno Y mismo objetivo
      2) mismo horario de entreno (el objetivo puede variar)
      3) mismo objetivo (el horario puede variar)
    Devuelve la primera candidata encontrada, o None si no hay nadie disponible.
    """
    candidatas = usuarias_sin_pareja(excluir=usuario)

    exacta = candidatas.filter(
        horario_preferido=usuario.horario_preferido, objetivo=usuario.objetivo
    ).first()
    if exacta:
        return exacta

    por_horario = candidatas.filter(horario_preferido=usuario.horario_preferido).first()
    if por_horario:
        return por_horario

    return candidatas.filter(objetivo=usuario.objetivo).first()


def emparejar(usuario_1, usuario_2):
    """Crea el emparejamiento (pareja de compromiso) entre dos usuarias."""
    return CompaneraDeCompromiso.objects.create(usuario_1=usuario_1, usuario_2=usuario_2)
