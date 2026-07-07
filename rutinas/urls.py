from django.urls import path
from . import views

app_name = 'rutinas'

urlpatterns = [
    path('', views.rutinas_lista, name='rutinas_lista'),
    path('nueva/', views.rutina_nueva, name='rutina_nueva'),
    path('<int:rutina_id>/', views.rutina_detalle, name='rutina_detalle'),
    path('biblioteca/', views.biblioteca, name='biblioteca'),
]
