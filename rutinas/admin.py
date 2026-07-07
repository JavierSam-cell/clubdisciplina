from django.contrib import admin
from .models import Ejercicio, Rutina, RutinaEjercicio


@admin.register(Ejercicio)
class EjercicioAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'grupo_muscular', 'video_url')
    list_filter = ('grupo_muscular',)
    search_fields = ('nombre',)


class RutinaEjercicioInline(admin.TabularInline):
    """Permite armar la rutina (agregar ejercicios en orden) desde la misma pantalla."""
    model = RutinaEjercicio
    extra = 3


@admin.register(Rutina)
class RutinaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'categoria', 'lugar', 'nivel', 'equipo', 'minutos_duracion')
    list_filter = ('categoria', 'lugar', 'nivel', 'equipo')
    inlines = [RutinaEjercicioInline]
