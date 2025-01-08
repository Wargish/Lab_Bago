from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .forms import MantenimientoForm
from .models import MantenimientoPreventivo, TareaMantenimiento

@login_required
def lista_mantenimiento(request):
    estado_selec = request.GET.get('estado', 'todos')
    if estado_selec == 'todos':
        mantenimientos = MantenimientoPreventivo.objects.all()
    else:
        mantenimientos = MantenimientoPreventivo.objects.filter(tarea_mantenimiento__estado=estado_selec)
    return render(request, 'lista_mant.html', {'mantenimientos': mantenimientos, 'estado_selec': estado_selec})

@login_required
def crear_informe(request):
    if request.user.groups.filter(name='supervisor').exists() or request.user.groups.filter(name='tecnico').exists() or request.user.groups.filter(name='externo').exists():
        if request.method == 'POST':
            form = MantenimientoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('lista_mantenimiento')
        else:
            form = MantenimientoForm()
        return render(request, 'crear_informe.html', {'form': form})
    else:
        return redirect('lista_mantenimiento')

@login_required
def modificar_informe(request, pk):
    informe = get_object_or_404(MantenimientoPreventivo, pk=pk)
    if request.user.groups.filter(name='supervisor').exists():
        if request.method == 'POST':
            form = MantenimientoForm(request.POST, instance=informe)
            if form.is_valid():
                form.save()
                return redirect('lista_mantenimiento')
        else:
            form = MantenimientoForm(instance=informe)
        return render(request, 'modificar_informe.html', {'form': form})
    else:
        return redirect('lista_mantenimiento')

@login_required
def cerrar_tarea(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    if request.user.groups.filter(name='supervisor').exists():
        tarea.estado = 'Archivada'
        tarea.save()
    return redirect('lista_mantenimiento')