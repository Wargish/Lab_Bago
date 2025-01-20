from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group
from .forms import *
from .models import *

from django.template.loader import render_to_string
from xhtml2pdf import pisa
from io import BytesIO
from django.conf import settings
import os

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
@group_required('Técnico', 'Externo')
def crear_informe(request, tarea_id):
    tarea = get_object_or_404(TareaMantenimiento, id=tarea_id)

    if request.method == 'POST':
        form = MantenimientoForm(request.POST)

        # Recoge los datos de la tabla dinámica
        tabla_dinamica = []
        total_filas = int(request.POST.get('tabla_dinamica_total', 0))
        for i in range(total_filas):
            refaccion = request.POST.get(f'tabla-{i}-refacción')
            medidas = request.POST.get(f'tabla-{i}-medidas')
            cantidad = request.POST.get(f'tabla-{i}-cantidad')

            if refaccion and medidas and cantidad:
                tabla_dinamica.append({
                    'refacción': refaccion,
                    'medidas': medidas,
                    'cantidad': cantidad,
                })

        if form.is_valid():
            informe = form.save(commit=False)
            informe.tarea_mantenimiento = tarea
            informe.tabla_dinamica = tabla_dinamica  # Guarda la tabla como JSON
            informe.save()
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Informe creado', text='Informe creado correctamente')
            return redirect('lista_mantenimiento')
        else:
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')

    else:
        form = MantenimientoForm()

    return render(request, 'crear_informe.html', {'form': form, 'tarea': tarea})


@login_required
@group_required('Supervisor')
def modificar_informe(request, pk):
    informe = get_object_or_404(MantenimientoPreventivo, pk=pk)
    if request.method == 'POST':
        form = MantenimientoForm(request.POST, instance=informe)
        
        # Recoge los datos de la tabla dinámica
        tabla_dinamica = []
        total_filas = int(request.POST.get('tabla_dinamica_total', 0))
        for i in range(total_filas):
            refaccion = request.POST.get(f'tabla-{i}-refacción')
            medidas = request.POST.get(f'tabla-{i}-medidas')
            cantidad = request.POST.get(f'tabla-{i}-cantidad')

            if refaccion and medidas and cantidad:
                tabla_dinamica.append({
                    'refacción': refaccion,
                    'medidas': medidas,
                    'cantidad': cantidad,
                })

        if form.is_valid():
            informe = form.save(commit=False)
            informe.tabla_dinamica = tabla_dinamica  # Guarda la tabla como JSON
            informe.save()
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Informe modificado', text='Informe modificado correctamente')
            return redirect('lista_mantenimiento')
        else:
            sweetify.error(request, 'Error', text='error en los campos.')
    else:
        form = MantenimientoForm(instance=informe)
    
    return render(request, 'modificar_informe.html', {
        'form': form,
        'informe': informe,
    })

@login_required
@group_required('Supervisor')
def cerrar_tarea(request, pk):
    tarea = get_object_or_404(TareaMantenimiento, pk=pk)
    tarea.estado = 'Archivada'
    tarea.save()
    sweetify.sweetalert(request, icon='warning', persistent='Ok', title='Tarea cerrada', text='La tarea ha sido cerrada y el informe solo estará disponible para su vista.')
    return redirect('lista_mantenimiento')

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths for xhtml2pdf
    """
    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

def generar_pdf_mantenimiento(tarea):
    # Get the associated maintenance report
    informe = MantenimientoPreventivo.objects.get(tarea_mantenimiento=tarea)
    
    # Prepare context data for the template
    context = {
        'tarea': tarea,
        'informe': informe,
        'fecha': tarea.creada.strftime('%d/%m/%Y'),
    }

    # Render the HTML template
    html = render_to_string('app/plantillas/pdf_prev.html', context)
    
    # Create PDF in memory
    buffer = BytesIO()
    pdf = pisa.CreatePDF(html, dest=buffer, link_callback=link_callback)
    
    if pdf.err:
        return None
    
    buffer.seek(0)
    return buffer.getvalue()

@login_required
@group_required('Supervisor', 'Técnico', 'Externo')
def ver_pdf(request, tarea_id):
    tarea = get_object_or_404(TareaMantenimiento, id=tarea_id)
    
    # Generate PDF
    pdf = generar_pdf_mantenimiento(tarea)
    if pdf:
        # Return PDF as response
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="mantenimiento_{tarea_id}.pdf"'
        response.write(pdf)
        return response
    else:
        # Handle error
        sweetify.error(request, 'Error', text='Error generando el PDF')
        return redirect('lista_mantenimiento')