from django.urls import path
from .views import *



urlpatterns = [

    path('api/user/<int:user_id>/', obtener_datos_usuario, name='obtener_datos_usuario'),

    path('dashboard/listar_solicitudes', listar_solicitudes, name='listar_solicitudes'),

    path('infraestructura/crear_solicitud/', crear_solicitud_externo, name='crear_solicitud'),
    path('infraestructura/presupuesto/<int:tarea_id>/', cargar_presupuesto, name='gestionar_presupuesto'),
    path('infraestructura/reporte_externo/<int:tarea_id>/', reporte_externo, name='reporte_externo'),
    path('infraestructura/feedback_externo/<int:tarea_id>/', feedback_externo, name='feedback_externo'),

    path('detalle_externo/solicitud/<int:solicitud_id>/', detalle_solicitud, name='detalle_solicitud'),
    path('detalle_externo/presupuesto_ext/<int:presupuesto_id>/', detalle_presupuesto, name='detalle_presupuesto'),
    path('detalle_externo/reporte_ext/<int:reporte_ex_id>/', detalle_reporte_ex, name='detalle_reporte_ext'),
    path('detalle_externo/feedback_ext/<int:feedback_ex_id>/', detalle_feedbacks_ex, name='detalle_feedback_ext'),
]