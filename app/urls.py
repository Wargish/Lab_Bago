from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name="home"),
    path('base/', base, name="base"),
    path('logout/', cerrar_session, name="logout"),

    path('auth/login/', iniciar_session, name="login"),
    path('auth/registro/', registro, name="registro"),
    path('auth/roles/', roles, name='roles'),


    path('infraestructura/Informe', informe, name='Informe'),
    path('infraestructura/reporte', reporte, name='reporte'),
    path('infraestructura/feedback', feedback, name='feedback'),
    path('infraestructura/crear_solicitud/', crear_solicitud_externo, name='crear_solicitud'),
    path('infraestructura/presupuesto/<int:solicitud_id>/', cargar_presupuesto, name='gestionar_presupuesto'),
    path('api/user/<int:user_id>/', obtener_datos_usuario, name='obtener_datos_usuario'),
    path('dashboard/listar_solicitudes', listar_solicitudes, name='listar_solicitudes'),



    path('dashboard/graficos', graficos, name='graficos'),
    path('dashboard/listar_tareas', listar_tareas, name='listar_tareas'),

    path('notificaciones/', notificaciones, name='notificaciones'),
    path('notificaciones/<int:notificaciones_id>/', notificaciones_id , name='notificaciones_id'),
    path('notificacion/marcar_leida/<int:notificacion_id>/', marcar_notificacion_leida, name='marcar_notificacion_leida'),



    path('detalle/informe/<int:informe_id>/', detalle_informe, name='detalle_informe'),
    path('detalle/reporte/<int:reporte_id>/', detalle_reporte, name='detalle_reporte'),
    path('detalle/feedback/<int:feedback_id>/', detalle_feedback, name='detalle_feedback'),

    path('error404/', error404, name='error404'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

