from django.contrib import admin
from .models import Comida, Dieta, DietaComida


@admin.register(Comida)
class ComidaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'momento_sugerido', 'calorias_aprox')
    list_filter = ('momento_sugerido',)
    search_fields = ('nombre',)


class DietaComidaInline(admin.TabularInline):
    """Permite armar el menú del día (agregar comidas en orden) desde la misma pantalla."""
    model = DietaComida
    extra = 4


@admin.register(Dieta)
class DietaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'objetivo', 'preferencia', 'presupuesto', 'comidas_por_dia')
    list_filter = ('categoria', 'objetivo', 'preferencia', 'presupuesto')
    inlines = [DietaComidaInline]
