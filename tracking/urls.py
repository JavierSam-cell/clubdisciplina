from django.urls import path
from . import views

app_name = 'tracking'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('registro-diario/', views.check_in_hoy, name='check_in'),
    path('fotos-progreso/', views.fotos_progreso, name='fotos_progreso'),
    path('fotos-progreso/comparar/', views.comparacion_progreso, name='comparacion_progreso'),
]
