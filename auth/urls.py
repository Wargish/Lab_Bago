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
    path('error404/', error404, name='error404'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


