from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from .forms import *
from .models import *

import sweetify

def group_required(*group_names):
    def in_groups(u):
        return u.is_authenticated and bool(u.groups.filter(name__in=group_names))
    return user_passes_test(in_groups)

@login_required
@group_required('Supervisor','Técnico','Externo')
def lista_mantenimiento(request):
    estado_selec = request.GET.get('estado', 'todos')
    estados_validos = ['En Curso', 'Revision', 'Archivada']

    user_roles = request.user.groups.values_list('name', flat=True)
    is_superuser = request.user.is_superuser

    tareas_mantenimiento = TareaMantenimiento.objects.all()

    if not is_superuser:
        if 'Externo' in user_roles or 'Técnico' in user_roles:
            tareas_mantenimiento = tareas_mantenimiento.filter(asignado_a=request.user)
        elif 'Supervisor' in user_roles:
            tareas_mantenimiento = tareas_mantenimiento.all()

    if estado_selec != 'todos' and estado_selec in estados_validos:
        tareas_mantenimiento = tareas_mantenimiento.filter(estado=estado_selec)

    return render(request, 'lista_mant.html', {
        'tareas_mantenimiento': tareas_mantenimiento,
        'estado_selec': estado_selec,
        'es_externo': 'Externo' in user_roles,
        'es_supervisor': 'Supervisor' in user_roles,
        'es_tecnico': 'Técnico' in user_roles,
    })

@login_required
@group_required('Supervisor')
def agregar_tarea(request):
    if request.method == 'POST':
        form = TareaMantenimientoForm(request.POST)
        if form.is_valid():
            tarea = form.save(commit=False)
            tarea.creado_por = request.user
            tarea.save()
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Tarea creada', text='Tarea creada correctamente')
            return redirect('lista_mantenimiento')
        else:
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')
    else:
        form = TareaMantenimientoForm()
    return render(request, 'tarea_mant.html', {'form': form})

@login_required
@group_required('Técnico','Externo')
def crear_informe(request):
    if request.method == 'POST':
        form = MantenimientoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('lista_mantenimiento')
    else:
        form = MantenimientoForm()
    return render(request, 'crear_informe.html', {'form': form})

@login_required
@group_required('Supervisor')
def modificar_informe(request, pk):
    informe = get_object_or_404(MantenimientoPreventivo, pk=pk)
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=informe)
        if form.is_valid():
            form.save()
            return redirect('lista_mantenimiento')
    else:
        form = MantenimientoForm(instance=informe)
    return render(request, 'modificar_informe.html', {'form': form})

@login_required
@group_required('Supervisor')
def cerrar_tarea(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    tarea.estado = 'Archivada'
    tarea.save()
    return redirect('lista_mantenimiento')