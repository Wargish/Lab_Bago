# Importaciones estándar de Django
from django.shortcuts import render, redirect, get_object_or_404,HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse
from django.core.cache import cache
from django.http import JsonResponse
from .signals import *
import sweetify
import os

# Importaciones para graficos
import plotly.express as px
import pandas as pd
from datetime import timedelta

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


# Vistas de autenticación y gestión de usuarios
def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                sweetify.sweetalert(request, icon='success', persistent='Ok', title='Registro exitoso', text='Usuario creado correctamente')
                return redirect('login')
            except Exception as e:
                form.add_error(None, f'Hubo un problema al crear el usuario: {str(e)}')
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
                sweetify.sweetalert(request, icon='success', title='Bienvenido', text='Inicio de sesión exitoso')
                return redirect('home')
            else:
                sweetify.error(request, 'Error', text='Usuario o contraseña incorrectos.')
        else:
            if 'captcha' in form.errors:
                sweetify.error(request, 'Error', text='Captcha inválido. Por favor, inténtalo de nuevo.')
            else:
                sweetify.error(request, 'Error', text='Usuario o contraseña incorrectos.')
    else:
        form = LoginForm()
    return render(request, "app/auth/login.html", {'form': form})

def cerrar_session(request):
    logout(request)
    sweetify.sweetalert(request, icon='success', title='Sesión cerrada', text='Has cerrado sesión exitosamente.')
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
            sweetify.error(request, 'Error', text='Error en el formulario.', persistent='Ok')
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
            return redirect('listar_solicitudes')
        else:
            sweetify.error(request, 'Error', text='Rellene los campos solicitados.')
    else:
        form = FeedbackForm(initial={'tarea': tarea})
    return render(request, 'app/infraestructura/feedback.html', {'form': form, 'tarea': tarea})


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

# Vistas de tareas y roles especiales
@login_required
@group_required('Operario', 'Supervisor', 'Técnico')
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


@login_required
@user_passes_test(lambda u: u.is_superuser or u.groups.filter(name='Supervisor').exists())
def graficos(request):
    # Cache the graphs for 1 hour to avoid recalculating them on every request
    cached_graphs = cache.get('dashboard_graphs')
    if cached_graphs:
        return render(request, "app/dashboard/graficos.html", cached_graphs)

    # **1. Tareas Completadas vs. Rechazadas**
    
        # Obtener las tareas con sus estados y ubicaciones
    tareas = Tarea.objects.all().select_related('estado', 'informe__ubicacion')

    # Filtrar y agrupar las tareas en los dos estados: Aceptada y Rechazada
    accepted_states = ['Completada', 'Archivada']
    rejected_state = 'Rechazada'

    # Agrupar las tareas por ubicación y estado
    tareas_agrupadas = []
    ubicaciones = Ubicacion.objects.all()

    for ubicacion in ubicaciones:
        # Contar tareas aceptadas (Completada + Archivada)
        accepted_count = tareas.filter(informe__ubicacion=ubicacion, estado__nombre__in=accepted_states).count()
        # Contar tareas rechazadas
        rejected_count = tareas.filter(informe__ubicacion=ubicacion, estado__nombre=rejected_state).count()

        tareas_agrupadas.append({
            'ubicacion': ubicacion.nombre,
            'Aceptada': accepted_count,
            'Rechazada': rejected_count
        })

    # Convertir en DataFrame
    df_tareas_agrupadas = pd.DataFrame(tareas_agrupadas)

    # Crear gráfico de barras con Plotly
    graph_tareas_por_lugar = px.bar(
        df_tareas_agrupadas, 
        x='ubicacion', 
        y=['Aceptada', 'Rechazada'], 
        title='Cantidad de Tareas por Ubicación (Aceptada vs Rechazada)',
        labels={'Aceptada': 'Tareas Aceptadas', 'Rechazada': 'Tareas Rechazadas'},
        color_discrete_map={'Aceptada': '#4CAF50', 'Rechazada': '#F44336'},  # Verde para aceptadas, rojo para rechazadas
    )

    # Personalizar el gráfico
    graph_tareas_por_lugar.update_layout(
        template='plotly_white',
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family="Arial, sans-serif", color="black", size=14),
        title_font=dict(size=20, color='black', family='Arial, sans-serif'),
        xaxis_title="Ubicación",
        yaxis_title="Cantidad de Tareas",
        xaxis_tickangle=-45,
        showlegend=True,  # Mostrar leyenda
        barmode='group',  # Colocar las barras en grupos (uno al lado del otro)
        legend_title_text='Estado de la Tarea'  # Título de la leyenda
    )

    # Convertir el gráfico a HTML
    graph_tareas_por_lugar_html = graph_tareas_por_lugar.to_html(full_html=False)

    # **2. Volumen de Tareas por Tiempo**
    df_tareas_time = pd.DataFrame(list(tareas.values('creado_en')))
    df_tareas_time['creado_en'] = pd.to_datetime(df_tareas_time['creado_en'])
    df_grouped_time = df_tareas_time.groupby(df_tareas_time['creado_en'].dt.date).size().reset_index(name='Cantidad')
    graph_volumen_tareas_tiempo = px.line(
        df_grouped_time, 
        x='creado_en', 
        y='Cantidad', 
        title='Volumen de Tareas por Tiempo',
        markers=True,  # Agregar marcadores en los puntos de datos
        line_shape='linear',  # Asegurarse de que la línea sea recta
        color_discrete_sequence=['#800080'],  # Morado para la línea
    )
    graph_volumen_tareas_tiempo.update_layout(
        template='plotly_white',  # Fondo blanco
        plot_bgcolor='white',  # Fondo blanco para el gráfico
        paper_bgcolor='white',  # Fondo blanco para el área fuera del gráfico
        font=dict(family="Arial, sans-serif", color="black", size=14),  # Fuente y color negro
        xaxis_title="Fecha de Creación",
        yaxis_title="Cantidad de Tareas",
        title_font=dict(size=20, color='black', family='Arial, sans-serif'),  # Título en negro
        xaxis_tickangle=-45,  # Rotar las fechas para mayor legibilidad
        showlegend=False  # Desactivar leyenda
    )
    graph_volumen_tareas_tiempo_html = graph_volumen_tareas_tiempo.to_html(full_html=False)

    # **3. Distribución de Tareas por Técnico**
    df_tecnico = pd.DataFrame(list(tareas.values('asignado_a__username')))
    task_counts_tecnico = df_tecnico['asignado_a__username'].value_counts().reset_index()
    task_counts_tecnico.columns = ['asignado_a', 'Cantidad']
    graph_distribucion_tecnico = px.pie(
        task_counts_tecnico, 
        names='asignado_a', 
        values='Cantidad', 
        title='Distribución de Tareas por Técnico',
        hole=0.3,  # Hacer un gráfico de dona
        color='asignado_a',  # Colorear por técnico
        color_discrete_sequence=px.colors.sequential.Purp  # Usar paleta de colores morados
    )
    graph_distribucion_tecnico.update_layout(
        template='plotly_white',  # Fondo blanco
        plot_bgcolor='white',  # Fondo blanco para el gráfico
        paper_bgcolor='white',  # Fondo blanco para el área fuera del gráfico
        font=dict(family="Arial, sans-serif", color="black", size=14),  # Fuente y color negro
        title_font=dict(size=20, color='black', family='Arial, sans-serif'),  # Título en negro
        showlegend=True  # Mostrar leyenda
    )
    graph_distribucion_tecnico_html = graph_distribucion_tecnico.to_html(full_html=False)

    # **4. Cantidad Histórica de Informes por Lugar**
    informes = Informe.objects.all()
    df_informes = pd.DataFrame(list(informes.values('ubicacion__nombre', 'creado_en')))
    df_informes_grouped = df_informes.groupby('ubicacion__nombre').size().reset_index(name='Cantidad')
    graph_informes_por_lugar = px.bar(
        df_informes_grouped, 
        x='ubicacion__nombre', 
        y='Cantidad', 
        title='Cantidad Histórica de Informes por Lugar',
        color='ubicacion__nombre',  # Colorear por ubicación
        color_discrete_map={ubicacion: '#800080' for ubicacion in df_informes_grouped['ubicacion__nombre']}  # Usar morado para cada ubicación
    )
    graph_informes_por_lugar.update_layout(
        template='plotly_white',  # Fondo blanco
        plot_bgcolor='white',  # Fondo blanco para el gráfico
        paper_bgcolor='white',  # Fondo blanco para el área fuera del gráfico
        font=dict(family="Arial, sans-serif", color="black", size=14),  # Fuente y color negro
        xaxis_title="Ubicación",
        yaxis_title="Cantidad de Informes",
        title_font=dict(size=20, color='black', family='Arial, sans-serif'),  # Título en negro
        xaxis_tickangle=-45,  # Rotar las etiquetas para mejorar la visibilidad
        showlegend=False  # Desactivar leyenda
    )
    graph_informes_por_lugar_html = graph_informes_por_lugar.to_html(full_html=False)

    # Prepare context with all graphs
    context = {
        'graph_tareas_por_lugar': graph_tareas_por_lugar_html,
        'graph_volumen_tareas_tiempo': graph_volumen_tareas_tiempo_html,
        'graph_distribucion_tecnico': graph_distribucion_tecnico_html,
        'graph_informes_por_lugar': graph_informes_por_lugar_html
    }

    # Cache the graphs for 1 hour
    cache.set('dashboard_graphs', context, timeout=3600)

    return render(request, "app/dashboard/graficos.html", context)



# Vistas de detalles (informes, reportes, feedbacks)
@login_required
@group_required('Operario', 'Supervisor', 'Técnico')
def detalle_informe(request, informe_id):
    informe = get_object_or_404(Informe, id=informe_id)
    return render(request, 'app/detalle/informe.html', {'informe': informe})

@login_required
@group_required('Operario', 'Supervisor', 'Técnico')
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(ReporteTarea, id=reporte_id)
    return render(request, 'app/detalle/reporte.html', {'reporte': reporte})

@login_required
@group_required('Operario', 'Supervisor', 'Técnico')
def detalle_feedback(request, feedback_id):
    feedback = get_object_or_404(FeedbackTarea, id=feedback_id)
    return render(request, 'app/detalle/feedback.html', {'feedback': feedback})


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

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import PresupuestoExternoForm
from .models import TareaExterno

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
        form = PresupuestoExternoForm()

    return render(request, 'app/infraestructura/presupuesto.html', {'form': form, 'tarea': tarea})

@login_required
@group_required('Operario', 'Supervisor', 'Externo')
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











# Vistas de error
def error_404(request):
    return render(request, "app/error/404.html", status=404)





