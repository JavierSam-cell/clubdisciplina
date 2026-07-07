from django.urls import path
from . import views

app_name = 'dietas'

urlpatterns = [
    path('', views.dietas_lista, name='dietas_lista'),
    path('nueva/', views.dieta_nueva, name='dieta_nueva'),
    path('<int:dieta_id>/', views.dieta_detalle, name='dieta_detalle'),
]
