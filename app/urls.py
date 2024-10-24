from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name="home"),
    path('base/', base, name="base"),
    path('auth/login/', login, name="login"),
    path('logout/', logout, name="logout"),
    path('auth/registro/', registro, name="registro"),
    path('infraestructura/informe', informe, name='informe'),
    path('infraestructura/reporte', reporte, name='reporte'),
    path('dashboard/graficos', graficos, name='graficos'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)