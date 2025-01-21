from django.urls import path
from django.conf.urls import handler404
from .views import *
from django.conf import settings
from django.conf.urls.static import static
from axes.decorators import axes_dispatch


urlpatterns = [
    path('', home, name="home"),
    path('base/', base, name="base"),
    #path('logout/', cerrar_session, name="logout"),

    #path('auth/login/', axes_dispatch(iniciar_session), name="login"),
    #path('auth/registro/', registro, name="registro"),
    path('auth/roles', roles, name='roles'),
    





    #path('infraestructura/crear_solicitud/', crear_solicitud_externo, name='crear_solicitud'),
    #path('infraestructura/presupuesto/<int:tarea_id>/', cargar_presupuesto, name='gestionar_presupuesto'),
    #path('infraestructura/reporte_externo/<int:tarea_id>/', reporte_externo, name='reporte_externo'),
    #path('infraestructura/feedback_externo/<int:tarea_id>/', feedback_externo, name='feedback_externo'),

    #path('api/user/<int:user_id>/', obtener_datos_usuario, name='obtener_datos_usuario'),

    path('dashboard/graficos', graficos, name='graficos'),
    path('descargar-tareas', descargar_tareas, name='descargar_tareas'),

    #path('dashboard/listar_tareas', listar_tareas, name='listar_tareas'),
    #path('dashboard/listar_solicitudes', listar_solicitudes, name='listar_solicitudes'),

    #path('notificaciones/', notificaciones, name='notificaciones'),
    #path('notificaciones/<int:notificaciones_id>/', notificaciones_id , name='notificaciones_id'),
    #path('notificacion/marcar_leida/<int:notificacion_id>/', marcar_notificacion_leida, name='marcar_notificacion_leida'),



    #path('detalle/informe/<int:informe_id>/', detalle_informe, name='detalle_informe'),
    #path('detalle/reporte/<int:reporte_id>/', detalle_reporte, name='detalle_reporte'),
    #path('detalle/feedback/<int:feedback_id>/', detalle_feedback, name='detalle_feedback'),

    #path('detalle_externo/solicitud/<int:solicitud_id>/', detalle_solicitud, name='detalle_solicitud'),
    #path('detalle_externo/presupuesto_ext/<int:presupuesto_id>/', detalle_presupuesto, name='detalle_presupuesto'),
    #path('detalle_externo/reporte_ext/<int:reporte_ex_id>/', detalle_reporte_ex, name='detalle_reporte_ext'),
    #path('detalle_externo/feedback_ext/<int:feedback_ex_id>/', detalle_feedbacks_ex, name='detalle_feedback_ext'),

    path('app/error/404', error_404, name='error_404'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


handler404 = error_404
