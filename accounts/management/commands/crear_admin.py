from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Crea usuario administrador inicial"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        username = "admin"
        email = "fjmme25@gmail.com"
        password = "admin123"

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING("El usuario admin ya existe")
            )
        else:
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )

            self.stdout.write(
                self.style.SUCCESS("Administrador creado correctamente")
            )