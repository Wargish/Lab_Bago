from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name="home"),
    path('base/', base, name="base"),
    path('logout/', Cerrar_session, name="logout"),

    path('auth/login/', iniciar_session, name="login"),
    path('auth/registro/', registro, name="registro"),
    path('auth/admin', admin, name='admin'),

    path('infraestructura/InformeCondiciones', informe, name='InformeCondiciones'),
    path('infraestructura/reporte', reporte, name='reporte'),

    path('dashboard/graficos', graficos, name='graficos'),
    path('dashboard/listar_tareas', listar_tareas, name='listar_tareas'),
    path('dashboard/feedback', feedback, name='feedback'),


    path('notificaciones/marcar/<int:notificacion_id>/', marcar_notificacion_como_leida, name='marcar_notificacion_como_leida'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)