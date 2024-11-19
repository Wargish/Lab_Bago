# Importaciones estándar de Django
from django.shortcuts import render, redirect, get_object_or_404,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
import sweetify

# Importaciones para graficos
import plotly.express as px
import pandas as pd
from datetime import timedelta

# Importaciones locales (formularios y modelos)
from .forms import *
from .models import *

# Filtro de grupos
def group_required(*group_names):
    def in_groups(u):
        return u.is_authenticated and bool(u.groups.filter(name__in=group_names))
    return user_passes_test(in_groups)


# Vistas básicas
def base(request):
    return render(request, "app/base.html")

def error404(request):
    return render(request, "app/404.html")

def home(request):
    username = None
    grupos = []

    if request.user.is_authenticated:
        username = request.user.username 
        grupos = request.user.groups.values_list('name', flat=True)

    return render(request, "app/home.html", {'username': username, 'grupos': grupos})


# Vistas de autenticación y gestión de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = RegistroForm()
    return render(request, "app/auth/registro.html", {'form': form})

def iniciar_session(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                sweetify.sweetalert(request, icon='success', persistent='Ok', title='Bienvenido', text='Inicio de sesión exitoso')
                return redirect('home')
        else:
            sweetify.error(request, 'Error', text='Usuario o contraseña incorrectos.', persistent='Ok')
    else:
        form = LoginForm()
    return render(request, "app/auth/login.html", {'form': form})

def cerrar_session(request):
    logout(request)
    return redirect('home')

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
            pass
        elif action == 'assign_task':
            tarea_id = request.POST.get('task_id')
            tarea = get_object_or_404(Tarea, id=tarea_id)
            tarea.asignar_tecnico(usuario)

    usuarios = User.objects.all()
    roles = Group.objects.all()
    tareas_sin_tecnico = Tarea.objects.filter(asignado_a__isnull=True)

    return render(request, "app/auth/roles.html", {'usuarios': usuarios, 'roles': roles, 'tareas_sin_tecnico': tareas_sin_tecnico})


# Vistas de CRUD y movimiento de información
@login_required
@group_required('Operario', 'Técnico', 'Externo', 'Supervisor')
def informe(request):
    if request.method == 'POST':
        form = InformeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('listar_tareas')
    else:
        form = InformeForm()
    return render(request, "app/infraestructura/Informe.html", {'form': form})

@login_required
@group_required('Operario', 'Técnico', 'Externo', 'Supervisor')
def reporte(request):
    tarea_id = request.GET.get('tarea_id')
    if not tarea_id:
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

            return redirect('home')
        else:
            # Si el formulario no es válido, muestra los errores
            print("Errores en el formulario:", form.errors)
    else:
        form = ReporteForm(initial={'tarea': tarea})

    return render(request, "app/infraestructura/reporte.html", {
        'form': form,
        'tarea': tarea,
        'tarea_id': tarea.id
    })


@login_required
@group_required('Operario', 'Técnico', 'Externo', 'Supervisor')
def feedback(request):
    tarea_id = request.GET.get('tarea_id')
    if not tarea_id:
        return redirect('listar_tareas')
    
    tarea = get_object_or_404(Tarea, id=tarea_id)

    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.tarea = tarea
            feedback.usuario = request.user
            feedback.save()
            return redirect('home')
        else:
            print("Errores en el formulario:", form.errors)
    else:
        form = FeedbackForm(initial={'tarea': tarea})

    return render(request, "app/infraestructura/feedback.html", {
        'form': form,
        'tarea': tarea,
        'tarea_id': tarea.id
    })


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

# Vistas de tareas y roles especiales
@login_required
def listar_tareas(request):
    estado_selec = request.GET.get('estado', 'todos')
    estados_validos = ['Pendiente', 'En Curso', 'Completada', 'Rechazada', 'Archivar']
    tareas = Tarea.objects.none()  # Inicializa con un QuerySet vacío

    is_superuser = request.user.is_superuser
    is_tecnico = request.user.groups.filter(name='Técnico').exists()
    is_externo = request.user.groups.filter(name='Externo').exists()
    is_supervisor = request.user.groups.filter(name='Supervisor').exists()
    is_operario = request.user.groups.filter(name='Operario').exists()

    # Filtrar tareas según el estado seleccionado y el tipo de usuario
    if is_superuser:
        if estado_selec == 'todos':
            tareas = Tarea.objects.all()
        elif estado_selec in estados_validos:
            tareas = Tarea.objects.filter(estado__nombre=estado_selec)
    elif is_tecnico or is_externo:
        if estado_selec == 'todos':
            tareas = Tarea.objects.filter(asignado_a=request.user)
        elif estado_selec in estados_validos:
            tareas = Tarea.objects.filter(asignado_a=request.user, estado__nombre=estado_selec)
    elif is_supervisor or is_operario:
        if estado_selec == 'todos':
            tareas = Tarea.objects.filter(informe__usuario=request.user)
        elif estado_selec in estados_validos:
            tareas = Tarea.objects.filter(informe__usuario=request.user, estado__nombre=estado_selec)

    return render(request, "app/dashboard/listar_tareas.html", {
        'tareas': tareas,
        'estado_selec': estado_selec,
        'es_superusuario': is_superuser,
        'es_tecnico': is_tecnico,
        'es_externo': is_externo,
        'es_supervisor': is_supervisor,
        'es_operario': is_operario,
    })


# Vistas de Dashboard y Análisis
@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Supervisor').exists())
def graficos(request):
    # **1. Tareas Completadas vs. Rechazadas**
    tareas = Tarea.objects.all()
    df_tareas = pd.DataFrame(list(tareas.values('estado__nombre')))
    task_counts = df_tareas['estado__nombre'].value_counts().reset_index()
    task_counts.columns = ['Estado', 'Cantidad']
    graph_tareas_completadas_rechazadas = px.bar(task_counts, x='Estado', y='Cantidad', title='Tareas Completadas vs. Rechazadas')
    graph_tareas_completadas_rechazadas.update_layout(template='plotly_white')
    graph_tareas_completadas_rechazadas_html = graph_tareas_completadas_rechazadas.to_html(full_html=False)

    # **2. Volumen de Tareas por Tiempo**
    df_tareas_time = pd.DataFrame(list(tareas.values('creado_en')))
    df_tareas_time['creado_en'] = pd.to_datetime(df_tareas_time['creado_en'])
    df_grouped_time = df_tareas_time.groupby(df_tareas_time['creado_en'].dt.date).size().reset_index(name='Cantidad')
    graph_volumen_tareas_tiempo = px.line(df_grouped_time, x='creado_en', y='Cantidad', title='Volumen de Tareas por Tiempo')
    graph_volumen_tareas_tiempo.update_layout(template='plotly_white')
    graph_volumen_tareas_tiempo_html = graph_volumen_tareas_tiempo.to_html(full_html=False)

    # **3. Distribución de Tareas por Técnico**
    df_tecnico = pd.DataFrame(list(tareas.values('asignado_a__username')))
    task_counts_tecnico = df_tecnico['asignado_a__username'].value_counts().reset_index()
    task_counts_tecnico.columns = ['asignado_a', 'Cantidad']
    graph_distribucion_tecnico = px.pie(task_counts_tecnico, names='asignado_a', values='Cantidad', title='Distribución de Tareas por Técnico')
    graph_distribucion_tecnico.update_layout(template='plotly_white')
    graph_distribucion_tecnico_html = graph_distribucion_tecnico.to_html(full_html=False)

    # **4. Cantidad Histórica de Informes por Lugar**
    informes = informe.objects.all()
    df_informes = pd.DataFrame(list(informes.values('lugar__nombre', 'createdAt')))
    df_informes_grouped = df_informes.groupby('lugar__nombre').size().reset_index(name='Cantidad')
    graph_informes_por_lugar = px.bar(df_informes_grouped, x='lugar__nombre', y='Cantidad', title='Cantidad Histórica de Informes por Lugar')
    graph_informes_por_lugar.update_layout(template='plotly_white')
    graph_informes_por_lugar_html = graph_informes_por_lugar.to_html(full_html=False)

    # Pasamos todos los gráficos a la plantilla
    context = {
        'graph_tareas_completadas_rechazadas': graph_tareas_completadas_rechazadas_html,
        'graph_volumen_tareas_tiempo': graph_volumen_tareas_tiempo_html,
        'graph_distribucion_tecnico': graph_distribucion_tecnico_html,
        'graph_informes_por_lugar': graph_informes_por_lugar_html
    }

    return render(request, "app/dashboard/graficos.html", context)


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

