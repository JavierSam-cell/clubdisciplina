from django.contrib import admin
from .models import RegistroDiario, Medalla, MedallaObtenida, FotoProgreso


@admin.register(RegistroDiario)
class RegistroDiarioAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha', 'entreno', 'peso_kg', 'cintura_cm')
    list_filter = ('entreno', 'fecha')
    search_fields = ('usuario__username', 'usuario__nombre_para_mostrar')


@admin.register(Medalla)
class MedallaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tipo_condicion', 'valor_condicion')


@admin.register(MedallaObtenida)
class MedallaObtenidaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'medalla', 'fecha_obtenida')


@admin.register(FotoProgreso)
class FotoProgresoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'fecha')
