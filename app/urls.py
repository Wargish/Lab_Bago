from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name="home"),
    path('base/', base, name="base"),
    path('auth/login/', iniciar_session, name="login"),
    path('logout/', Cerrar_session, name="logout"),
    path('auth/registro/', registro, name="registro"),
    path('infraestructura/InformeCondiciones', informe, name='InformeCondiciones'),
    path('infraestructura/reporte', reporte, name='reporte'),
    path('dashboard/graficos', graficos, name='graficos'),
    path('auth/admin', admin, name='admin'),

    path('notificaciones/marcar/<int:notificacion_id>/', marcar_notificacion_como_leida, name='marcar_notificacion_como_leida'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)