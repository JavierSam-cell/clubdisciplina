from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    # Agregamos nuestros campos extra a las secciones ya existentes de UserAdmin
    fieldsets = UserAdmin.fieldsets + (
        ('Perfil del club', {
            'fields': (
                'nombre_para_mostrar', 'tono_mensajes', 'edad', 'estatura_cm',
                'peso_inicial_kg', 'cintura_inicial_cm', 'objetivo',
                'lugar_entreno', 'nivel', 'minutos_disponibles',
                'lesiones', 'horario_preferido', 'fecha_inicio_compromiso',
            )
        }),
    )
    list_display = ('username', 'nombre_para_mostrar', 'objetivo', 'tono_mensajes', 'is_staff')
