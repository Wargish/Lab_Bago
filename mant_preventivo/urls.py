from django.urls import path
from .views import *

urlpatterns = [
    path('', lista_mantenimiento, name='lista_mantenimiento'),
    path('crear/<int:tarea_id>/', crear_informe, name='crear_informe'),
    path('modificar/<int:pk>/', modificar_informe, name='modificar_informe'),
    path('cerrar/<int:pk>/', cerrar_tarea, name='cerrar_tarea'),
    path('tarea_mant/', agregar_tarea, name='tarea_mant'),
    path('ver_pdf/<int:tarea_id>/', ver_pdf, name='ver_pdf'),


]