from django.core.management.base import BaseCommand

from community.utils import usuarias_sin_pareja, buscar_companera_compatible, emparejar


class Command(BaseCommand):
    help = (
        "Empareja automáticamente a las usuarias que todavía no tienen compañera de "
        "compromiso, priorizando mismo horario de entreno y, si no hay coincidencia, "
        "mismo objetivo. Pensado para correrse periódicamente (ej. un cron semanal)."
    )

    def handle(self, *args, **options):
        procesadas = set()
        creadas = 0

        # Se congela la lista al inicio; conforme se van armando parejas,
        # cada quien deja de estar disponible para las siguientes vueltas.
        for usuario in list(usuarias_sin_pareja()):
            if usuario.id in procesadas:
                continue

            candidata = buscar_companera_compatible(usuario)
            if candidata is None:
                continue

            emparejar(usuario, candidata)
            procesadas.add(usuario.id)
            procesadas.add(candidata.id)
            creadas += 1
            self.stdout.write(self.style.SUCCESS(
                f"Emparejadas: {usuario} <-> {candidata} "
                f"(horario: {usuario.horario_preferido}/{candidata.horario_preferido}, "
                f"objetivo: {usuario.objetivo}/{candidata.objetivo})"
            ))

        if creadas == 0:
            self.stdout.write("No había usuarias pendientes por emparejar (o no hubo candidatas compatibles).")
        else:
            self.stdout.write(self.style.SUCCESS(f"Total de parejas nuevas creadas: {creadas}"))
