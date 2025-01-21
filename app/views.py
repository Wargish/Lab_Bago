# Importaciones estándar de Django
from django.shortcuts import render, redirect, get_object_or_404,HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.core.cache import cache
from .signals import *
import csv

# Importaciones locales (formularios y modelos)
from internal_workers.models import Tarea, Notificacion, Informe, Ubicacion


# Vistas básicas
def base(request):
    return render(request, "app/base.html")

def home(request):
    username = None
    grupos = []

    if request.user.is_authenticated:
        username = request.user.username 
        grupos = request.user.groups.values_list('name', flat=True)

    return render(request, "app/home.html", {'username': username, 'grupos': grupos})

# Vistas de notificaciones
@login_required
def notificaciones(request):
    notificaciones = Notificacion.objects.filter(user=request.user)
    return render(request, "app/notificaciones.html", {'notificaciones': notificaciones})

@login_required
def notificaciones_id(request, notificaciones_id):
    notificacion = Notificacion.objects.get(id=notificaciones_id)
    if notificacion.user == request.user:
        notificacion.marcar_como_leido()
    return HttpResponseRedirect(reverse('listar_tareas') + '?estado=Pendiente')

@login_required
def marcar_notificacion_leida(request, notificacion_id):
    notificacion = get_object_or_404(Notificacion, id=notificacion_id)
    if notificacion.usuario == request.user:
        notificacion.marcar_como_leido()
        return redirect('detalle_informe', informe_id=notificacion.informe.id)
    else:
        return redirect('home')



def graficos(request):
    return render(request, "app/dashboard/graficos.html")

def descargar_tareas(request):
    # Crear la respuesta HTTP con el archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="tareas.csv"'

    writer = csv.writer(response)

    # Obtener los nombres de las columnas del modelo Tarea
    field_names = [field.name for field in Tarea._meta.fields]
    writer.writerow(field_names)

    # Obtener los valores de las tareas
    tareas = Tarea.objects.all().values_list()
    for tarea in tareas:
        writer.writerow(tarea)

    return response



def error_404(request):
    return render (request, "app/error/404.html")