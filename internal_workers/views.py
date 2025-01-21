# Importaciones estándar de Django
from django.shortcuts import render, redirect, get_object_or_404,HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST

from django.http import JsonResponse
import sweetify
import json

# Importaciones locales (formularios y modelos)
from forms import InformeForm, ReporteForm, FeedbackForm
from models import Informe, Tarea, ReporteTarea, FeedbackTarea, Notificacion, Ubicacion 


# Filtro Grupos de Usuarios
def group_required(*group_names):
    def in_groups(u):
        return u.is_authenticated and bool(u.groups.filter(name__in=group_names))
    return user_passes_test(in_groups)



# Vistas de CRUD y movimiento de información
@login_required
@group_required('Operario','Supervisor')
def informe(request):
    if request.method == 'POST':
        form = InformeForm(request.POST, request.FILES)
        if form.is_valid():
            informe = form.save(commit=False)
            informe.usuario = request.user  # Asignar el usuario que crea el informe
            informe.save()
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Informe creado', text='Informe creado correctamente')
            return redirect('listar_tareas')
        else:
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')
    else:
        form = InformeForm()
    return render(request, "app/infraestructura/Informe.html", {'form': form})

@login_required
@group_required('Técnico')
def reporte(request):
    tarea_id = request.GET.get('tarea_id')
    if not tarea_id:
        sweetify.error(request, 'Error', text='No se ha especificado una tarea.', persistent='Ok')
        return redirect('listar_tareas')  # Si no hay tarea_id, redirigir a la lista

    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        form.fields['tarea'].initial = tarea  # Set the initial value for the tarea field

        # Verificar los archivos recibidos
        if form.is_valid():
            reporte = form.save(commit=False)  # Guardar el formulario sin commit
            reporte.tarea = tarea  # Asignar la tarea
            reporte.usuario = request.user  # Asignar el usuario actual
            reporte.save()  # Guardar el objeto con la tarea asignada
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Reporte creado', text='Reporte creado correctamente')
            return redirect('listar_tareas')
        else:
            # Si el formulario no es válido, muestra los errores
            sweetify.error(request, 'Error', text='Debe rellenar todos los campos.', persistent='Ok')
    else:
        form = ReporteForm(initial={'tarea': tarea})

    return render(request, "app/infraestructura/reporte.html", {
        'form': form,
        'tarea': tarea,
        'tarea_id': tarea.id
    })

@login_required
@group_required('Operario', 'Supervisor')
def feedback(request, tarea_id):
    tarea = get_object_or_404(Tarea, id=tarea_id)
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.tarea = tarea
            feedback.creado_por = request.user
            feedback.save()
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Feedback creado', text='Feedback creado correctamente')
            return redirect('listar_tareas')
        else:
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')
    else:
        form = FeedbackForm(initial={'tarea': tarea})
    return render(request, 'app/infraestructura/feedback.html', {'form': form, 'tarea': tarea})

# Vistas de tareas y roles especiales
@login_required
@group_required('Operario','Supervisor','Técnico')
def listar_tareas(request):
    estado_selec = request.GET.get('estado', 'todos')
    estados_validos = ['Pendiente', 'En Curso', 'Completada', 'Rechazada', 'Archivada']

    # Verificar tipo de usuario
    user_roles = request.user.groups.values_list('name', flat=True)
    is_superuser = request.user.is_superuser

    # Base queryset
    tareas = Tarea.objects.all()

    if not is_superuser:
        if 'Técnico' in user_roles:
            tareas = tareas.filter(asignado_a=request.user)
        elif 'Supervisor' in user_roles or 'Operario' in user_roles:
            tareas = tareas.filter(informe__usuario=request.user)

    # Filtrar por estado si aplica
    if estado_selec != 'todos' and estado_selec in estados_validos:
        tareas = tareas.filter(estado__nombre=estado_selec)

    return render(request, "app/dashboard/listar_tareas.html", {
        'tareas': tareas,
        'estado_selec': estado_selec,
        'es_superusuario': is_superuser,
        'es_tecnico': 'Técnico' in user_roles,
        'es_supervisor': 'Supervisor' in user_roles,
        'es_operario': 'Operario' in user_roles,
    })


# Vistas de detalles (informes, reportes, feedbacks)
@login_required
def detalle_informe(request, informe_id):
    informe = get_object_or_404(Informe, id=informe_id)
    return render(request, 'app/detalle/informe.html', {'informe': informe})

@login_required
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteTarea, id=reporte_id)
    return render(request, 'app/detalle/reporte.html', {'reporte': reporte})

@login_required
def detalle_feedback(request, feedback_id):
    feedback = get_object_or_404(FeedbackTarea, id=feedback_id)
    return render(request, 'app/detalle/feedback.html', {'feedback': feedback})


# Notificaciones
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

@require_POST
def agregar_ubicacion(request):
    try:
        data = json.loads(request.body)
        nombre = data.get('nombre')
        if not nombre:
            return JsonResponse({'success': False, 'error': 'Nombre es requerido'})
        
        ubicacion = Ubicacion.objects.create(nombre=nombre)
        return JsonResponse({
            'success': True,
            'id': ubicacion.id,
            'nombre': ubicacion.nombre
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
