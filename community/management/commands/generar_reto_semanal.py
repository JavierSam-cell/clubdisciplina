from django.core.management.base import BaseCommand

from community.utils import generar_semana_de_retos


class Command(BaseCommand):
    """
    Genera (o confirma que ya existe) la semana de retos vigente.

    NOTA: esto ya NO hace falta correrlo manualmente ni con cron. La app
    genera la semana sola, automáticamente, la primera vez que alguien
    entra al dashboard y no encuentra una semana vigente (ver
    `community.utils.reto_semanal_activo`). Este comando queda solo como
    utilidad opcional, por ejemplo si quieres adelantar/precrear la semana
    entrante desde la terminal antes de que nadie entre.
    """
    help = "Genera manualmente la semana de retos actual (opcional: la app ya la autogenera sola)."

    def handle(self, *args, **options):
        semana = generar_semana_de_retos()
        self.stdout.write(self.style.SUCCESS(
            f"Semana de retos lista: {semana.fecha_inicio} – {semana.fecha_fin}"
        ))
        for item in semana.items.all():
            self.stdout.write(f"  · [{item.get_categoria_display()}] {item.texto} ({item.puntos} pts)")
