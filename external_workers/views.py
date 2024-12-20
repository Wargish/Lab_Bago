# Importaciones estándar de Django
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse


import sweetify
import os

# Importaciones para PDF
from xhtml2pdf import pisa
from io import BytesIO
from reportlab.pdfgen import canvas
from django.core.files.base import ContentFile
from django.template.loader import render_to_string

# Importaciones locales (formularios y modelos)
from .forms import *
from .models import *


# Filtro de grupos
def group_required(*group_names):
    def in_groups(u):
        return u.is_authenticated and bool(u.groups.filter(name__in=group_names))
    return user_passes_test(in_groups)


def generar_pdf_peticion(solicitud):
    # Renderizar el HTML con los datos de la solicitud
    html = render_to_string('app/plantillas/pdf.html', {'solicitud': solicitud})

    # Crear un buffer en memoria para almacenar el PDF
    buffer = BytesIO()

    # Usar xhtml2pdf para convertir el HTML a PDF
    pisa_status = pisa.CreatePDF(html, dest=buffer, link_callback=link_callback)

    # Si la conversión es exitosa, devolver el contenido del PDF
    if pisa_status.err:
        return None
    
    # Reposicionar el puntero del buffer al inicio
    buffer.seek(0)

    return buffer.getvalue()

def link_callback(uri, rel):
    """
    Convert HTML URIs to absolute system paths so xhtml2pdf can access those resources
    """
    sUrl = settings.STATIC_URL  # Typically /static/
    sRoot = settings.STATIC_ROOT  # Typically /home/userX/project_static/
    mUrl = settings.MEDIA_URL  # Typically /media/
    mRoot = settings.MEDIA_ROOT  # Typically /home/userX/project_media/

    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri

    # Make sure that file exists
    if not os.path.isfile(path):
        raise Exception(
            'media URI must start with %s or %s' % (sUrl, mUrl)
        )
    return path

@login_required
@group_required('Operario', 'Supervisor')
def crear_solicitud_externo(request):
    if request.method == 'POST':
        form = SolicitudExternoForm(request.POST, request.FILES)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.externo = form.cleaned_data['externo']
            solicitud.creado_por = request.user
            solicitud.save()

            # Generar y guardar el PDF con xhtml2pdf
            pdf_content = generar_pdf_peticion(solicitud)
            if pdf_content:
                solicitud.pdf_peticion.save(f'peticion_{solicitud.id}.pdf', ContentFile(pdf_content))
                sweetify.sweetalert(request, icon='success', persistent='Ok', title='Solicitud creada', text='Solicitud creada correctamente')
            else:
                sweetify.error(request, 'Error', text='Hubo un error al generar el PDF.', persistent='Ok')

            return redirect('home')
    else:
        form = SolicitudExternoForm()
    
    return render(request, 'app/infraestructura/crear_solicitud.html', {'form': form})

@login_required
def obtener_datos_usuario(request, user_id):
    user = get_object_or_404(User, id=user_id)
    data = {
        'email': user.email,
    }
    return JsonResponse(data)


@login_required
@group_required('Operario', 'Supervisor')
def cargar_presupuesto(request, tarea_id):
    tarea = get_object_or_404(TareaExterno, id=tarea_id)
    if request.method == 'POST':
        form = PresupuestoExternoForm(request.POST, request.FILES)
        if form.is_valid():
            presupuesto = form.save(commit=False)
            presupuesto.tarea_externo = tarea
            presupuesto.creado_por = request.user
            presupuesto.save()

            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Presupuesto creado', text='Presupuesto creado correctamente')
            return redirect('listar_solicitudes')  # Cambiar por la vista adecuada
        else:
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')
    else:
        form = PresupuestoExternoForm()

    return render(request, 'app/infraestructura/presupuesto.html', {'form': form, 'tarea': tarea})

@login_required
def listar_solicitudes(request):
    estado_selec = request.GET.get('estado', 'todos')
    estados_validos = ['en_espera', 'en_curso', 'completada', 'rechazada']

    user_roles = request.user.groups.values_list('name', flat=True)
    is_superuser = request.user.is_superuser

    tareas_externo = TareaExterno.objects.all()

    if not is_superuser:
        if 'Externo' in user_roles:
            tareas_externo = tareas_externo.filter(solicitud__externo=request.user)
        elif 'Supervisor' in user_roles or 'Operario' in user_roles:
            tareas_externo = tareas_externo.filter(solicitud__creado_por=request.user)

    if estado_selec != 'todos' and estado_selec in estados_validos:
        tareas_externo = tareas_externo.filter(estado=estado_selec)

    return render(request, "app/dashboard/listar_solicitudes.html", {
        'tareas_externo': tareas_externo,
        'estado_selec': estado_selec,
        'es_superusuario': is_superuser,
        'es_externo': 'Externo' in user_roles,
        'es_supervisor': 'Supervisor' in user_roles,
        'es_operario': 'Operario' in user_roles,
    })

@login_required
@group_required('Externo')
def reporte_externo(request, tarea_id):
    tarea = get_object_or_404(TareaExterno, id=tarea_id)
    if request.method == 'POST':
        form = ExternoReporteForm(request.POST, request.FILES)
        if form.is_valid():
            reporte = form.save(commit=False)
            reporte.tarea_externo = tarea
            reporte.creado_por = request.user
            reporte.save()
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Reporte creado', text='Reporte creado correctamente')
            return redirect('listar_solicitudes')
        else:
            # Print form errors to the console for debugging
            print(form.errors)
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')
    else:
        form = ExternoReporteForm(initial={'tarea_externo': tarea})
    return render(request, 'app/infraestructura/reporte_externo.html', {'form': form, 'tarea': tarea})


@login_required
@group_required('Operario', 'Supervisor')
def feedback_externo(request, tarea_id):
    tarea = get_object_or_404(TareaExterno, id=tarea_id)
    if request.method == 'POST':
        form = ExternoFeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.tarea_externo = tarea
            feedback.creado_por = request.user
            feedback.save()
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Feedback creado', text='Feedback creado correctamente')
            return redirect('listar_solicitudes')
        else:
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')
    else:
        form = ExternoFeedbackForm(initial={'tarea_externo': tarea})
    return render(request, 'app/infraestructura/feedback_externo.html', {'form': form, 'tarea': tarea})

# Vistas de Externo (Solicitud, Presupuesto, reportes, feedbacks)
@login_required
def detalle_solicitud(request, solicitud_id):
    solicitud = get_object_or_404(SolicitudExterno, id=solicitud_id)
    return render(request, 'app/detalle_externo/solicitud.html', {'solicitud': solicitud})

@login_required
def detalle_presupuesto(request, presupuesto_id):
    presupuesto = get_object_or_404(PresupuestoExterno, id=presupuesto_id)
    return render(request, 'app/detalle_externo/presupuesto_ext.html', {'presupuesto': presupuesto})

@login_required
def detalle_reporte_ex(request, reporte_ex_id):
    reporte = get_object_or_404(ExternoReporte, id=reporte_ex_id)
    return render(request, 'app/detalle_externo/reporte_ext.html', {'reporte': reporte})

@login_required
def detalle_feedbacks_ex(request, feedback_ex_id):
    feedback = get_object_or_404(ExternoFeedback, id=feedback_ex_id)
    return render(request, 'app/detalle_externo/feedback_ext.html', {'feedback': feedback})

