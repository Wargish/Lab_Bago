# Importaciones estándar de Django
from django.shortcuts import render, redirect, get_object_or_404,HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.core.cache import cache
from .signals import *
import csv

# Importaciones para graficos
import plotly.express as px
import pandas as pd
from datetime import timedelta

# Importaciones locales (formularios y modelos)
from .forms import *
from internal_workers.models import Tarea, Notificacion

# Filtro de grupos
def group_required(*group_names):
    def in_groups(u):
        return u.is_authenticated and bool(u.groups.filter(name__in=group_names))
    return user_passes_test(in_groups)


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

@login_required
@user_passes_test(lambda u: u.is_superuser)
def roles(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        usuario_id = request.POST.get('user_id')
        usuario = get_object_or_404(User, id=usuario_id)

        if action == 'change_role':
            rol = request.POST.get('role')
            grupo = Group.objects.get(name=rol)
            usuario.groups.clear()
            grupo.user_set.add(usuario)
        elif action == 'delete_user':
            usuario.delete()
        elif action == 'modify_user':
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            usuario.username = username
            usuario.email = email
            if password:
                usuario.set_password(password)
            usuario.save()
        elif action == 'assign_task':
            tarea_id = request.POST.get('task_id')
            tarea = get_object_or_404(Tarea, id=tarea_id)
            tarea.asignar_tecnico(usuario)
    
    role_filter = request.GET.get('role', 'all')

    usuarios = User.objects.all()

    if role_filter != 'all':
        usuarios = usuarios.filter(groups__name=role_filter)

    roles = Group.objects.all()
    tareas_sin_tecnico = Tarea.objects.filter(asignado_a__isnull=True)

    context = {
        'usuarios': usuarios,
        'roles': roles,
        'tareas_sin_tecnico': tareas_sin_tecnico,
        'selected_role': role_filter,
    }

    return render(request, "app/auth/roles.html", {'usuarios': usuarios, 'roles': roles, 'tareas_sin_tecnico': tareas_sin_tecnico})

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


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Supervisor').exists())
def graficos(request):

    return render(request, "app/dashboard/graficos.html",)

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