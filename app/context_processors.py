from internal_workers.models import Notificacion

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
        notificaciones = Notificacion.objects.filter(usuario=request.user, leido=False).order_by('-creado_en')[:3]
    else:
        notificaciones = []
    return {'notificaciones': notificaciones}