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
from .models import *
from internal_workers.models import Tarea

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
            pass
        elif action == 'assign_task':
            tarea_id = request.POST.get('task_id')
            tarea = get_object_or_404(Tarea, id=tarea_id)
            tarea.asignar_tecnico(usuario)

    usuarios = User.objects.all()
    roles = Group.objects.all()
    tareas_sin_tecnico = Tarea.objects.filter(asignado_a__isnull=True)

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