from .models import Notificacion
from django.contrib.auth.models import Group

def user_groups(request):
    if request.user.is_authenticated:
        username = request.user.username
        grupos = request.user.groups.values_list('name', flat=True)
    else:
        username = None
        grupos = []
    return {
        'username': username,
        'grupos': grupos,
    }

def notificaciones(request):
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.filter(user=request.user, leido=False).order_by('-createdAt')[:3]
    else:
        notificaciones = []
    return {'notificaciones': notificaciones}