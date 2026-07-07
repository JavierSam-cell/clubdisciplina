from django.urls import path
from . import views

app_name = 'community'

urlpatterns = [
    path('', views.feed, name='feed'),
    path('post/<int:post_id>/reaccionar/', views.reaccionar, name='reaccionar'),

    path('recetas/', views.recetas_lista, name='recetas_lista'),
    path('recetas/nueva/', views.receta_nueva, name='receta_nueva'),
    path('recetas/<int:receta_id>/guardar/', views.receta_guardar, name='receta_guardar'),

    path('frases/', views.frases_lista, name='frases_lista'),
    path('frases/nueva/', views.frase_nueva, name='frase_nueva'),

    path('ranking/', views.ranking, name='ranking'),
    path('retos/item/<int:item_id>/completar/', views.marcar_item_completado, name='marcar_item_completado'),

    path('mi-companera/', views.mi_companera, name='mi_companera'),

    path('socios/', views.socios_lista, name='socios_lista'),
    path('socios/<int:socio_id>/banear/', views.socio_banear, name='socio_banear'),
    path('socios/<int:socio_id>/eliminar/', views.socio_eliminar, name='socio_eliminar'),
]
