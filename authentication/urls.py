from django.urls import path
from axes.decorators import axes_dispatch
from .views import *


urlpatterns = [

    path('logout/', cerrar_session, name="logout"),
    path('login/', axes_dispatch(iniciar_session), name="login"),
    path('registro/', registro, name="registro"),
    path('roles/', roles, name='roles'),
]