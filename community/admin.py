from django.contrib import admin
from .models import (
    Post, Reaccion, Receta, Frase,
    CompaneraDeCompromiso, MensajeCompanera,
    OpcionRetoBiblioteca, RetoSemanal, ItemRetoSemanal,
    ParticipacionItemReto, PuntosEvento,
)


@admin.action(description="Aprobar elementos seleccionados")
def aprobar(modeladmin, request, queryset):
    queryset.update(aprobado=True)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'tipo', 'creado')
    list_filter = ('tipo',)


@admin.register(Receta)
class RecetaAdmin(admin.ModelAdmin):
    # Este es el panel de moderación de recetas: lo primero que ves
    # son las que NO están aprobadas todavía.
    list_display = ('titulo', 'autor', 'categoria', 'aprobado', 'creado')
    list_filter = ('aprobado', 'categoria')
    actions = [aprobar]
    ordering = ['aprobado', '-creado']


@admin.register(Frase)
class FraseAdmin(admin.ModelAdmin):
    # Panel de moderación de frases compartidas por la comunidad.
    list_display = ('texto', 'origen', 'momento', 'compartida_por', 'aprobado')
    list_filter = ('origen', 'momento', 'aprobado')
    actions = [aprobar]
    ordering = ['aprobado', '-creado']


@admin.register(CompaneraDeCompromiso)
class CompaneraDeCompromisoAdmin(admin.ModelAdmin):
    list_display = ('usuario_1', 'usuario_2', 'activa', 'fecha_emparejamiento')


class ItemRetoSemanalInline(admin.TabularInline):
    model = ItemRetoSemanal
    extra = 0


@admin.register(RetoSemanal)
class RetoSemanalAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'fecha_inicio', 'fecha_fin', 'generado_automaticamente')
    inlines = [ItemRetoSemanalInline]


@admin.register(OpcionRetoBiblioteca)
class OpcionRetoBibliotecaAdmin(admin.ModelAdmin):
    # Aquí es donde se cargan las opciones posibles por categoría (la "biblioteca").
    list_display = ('texto', 'categoria', 'puntos', 'activo')
    list_filter = ('categoria', 'activo')


@admin.register(PuntosEvento)
class PuntosEventoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'puntos', 'motivo', 'detalle', 'creado')
    list_filter = ('motivo',)


admin.site.register(Reaccion)
admin.site.register(MensajeCompanera)
admin.site.register(ParticipacionItemReto)
