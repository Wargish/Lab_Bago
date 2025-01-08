from django.urls import path
from .views import *

urlpatterns = [
    path('', lista_mantenimiento, name='lista_mantenimiento'),
    path('crear/', crear_informe, name='crear_informe'),
    path('modificar/<int:pk>/', modificar_informe, name='modificar_informe'),
    path('cerrar/<int:pk>/', cerrar_tarea, name='cerrar_tarea'),
]