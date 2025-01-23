from django.urls import path
from .views import *



urlpatterns = [

    path('listar_tareas', listar_tareas, name='listar_tareas'),

    path('Informe', informe, name='Informe'),
    path('reporte', reporte, name='reporte'),
    path('feedback/<int:tarea_id>/', feedback, name='feedback'),
    
    path('detalle/informe/<int:informe_id>/', detalle_informe, name='detalle_informe'),
    path('detalle/reporte/<int:reporte_id>/', detalle_reporte, name='detalle_reporte'),
    path('detalle/feedback/<int:feedback_id>/', detalle_feedback, name='detalle_feedback'),

    path('notificaciones/', notificaciones, name='notificaciones'),
    path('notificaciones/<int:notificaciones_id>/', notificaciones_id , name='notificaciones_id'),
    path('notificacion/marcar_leida/<int:notificacion_id>/', marcar_notificacion_leida, name='marcar_notificacion_leida'),

    path('api/ubicaciones-tecnicas/', ubicaciones_tecnicas_por_zona, name='ubicaciones_tecnicas_por_zona'),
    path('api/equipos/', equipos_por_ubicacion_tecnica, name='equipos_por_ubicacion_tecnica'),

]