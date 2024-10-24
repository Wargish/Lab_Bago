from .models import Notificacion

def notificaciones(request):
    if request.user.is_authenticated:
        notificaciones = Notificacion.objects.filter(user=request.user, leido=False).order_by('-createdAt')[:3]
    else:
        notificaciones = []
    return {'notificaciones': notificaciones}