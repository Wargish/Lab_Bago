from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *

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
def admin(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        rol = request.POST.get('rol')
        usuario = get_object_or_404(User, id=usuario_id)
        
        grupo = Group.objects.get(name=rol)
        grupo.user_set.add(usuario)
    
    usuarios = User.objects.all()
    roles = Group.objects.all()

    return render(request, "app/auth/admin.html",{'usuarios': usuarios, 'roles': roles})

def iniciar_session(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = LoginForm()
    return render(request, "app/auth/login.html", {'form': form})

def Cerrar_session(request):
    logout(request)
    return redirect('home')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'app/auth/registro.html', {'form': form})

@login_required
def informe(request):
    if request.method == 'POST':
        form = InformeForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = InformeForm()
    return render(request, "app/infraestructura/InformeCondiciones.html", {'form': form})

@login_required
def reporte(request):
    if request.method == 'POST':
        form = ReporteForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ReporteForm()
    return render(request, "app/infraestructura/reporte.html", {'form': form})


@login_required
def marcar_notificacion_como_leida(request, notificacion_id):
    notificacion = Notificacion.objects.get(id=notificacion_id)
    if notificacion.user == request.user:
        notificacion.marcar_como_leido()


@login_required
def graficos(request):
    return render(request, "app/dashboard/graficos.html")

@login_required
def listar_tareas(request):
    estado_selec = request.GET.get('estado', 'todos')
    estados_validos = ['Pendiente', 'En Curso', 'Completada', 'Archivar']

    if estado_selec == 'todos':
        tareas = Tarea.objects.filter(tecnico=request.user)
    elif estado_selec in estados_validos:
        tareas = Tarea.objects.filter(tecnico=request.user ,estado=estado_selec)
    else:
        tareas = Tarea.objects.none()

    return render(request, "app/dashboard/listar_tareas.html", {
        'tareas': tareas,
        'estado_selec': estado_selec
    })

def feedback(request, tarea_id):
    tarea = Tarea.objects.get(id=tarea_id)
    if request.method == 'POST':
        conforme = request.POST.get('conforme') == 'True'
        comentario = request.POST.get('comentario')
        feedback = Feedback.objects.create(tarea=tarea, conforme=conforme, comentario=comentario)

        if conforme:
            tarea.archivar_si_conforme()
        else:
            tarea.rechazar_si_no_conforme(feedback)

    return redirect('app/dashboard/listar_tareas.html')






# Vistas personalizadas

@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Operarios', 'Supervisores']).exists())
def lista_tareas_operarios_supervisores(request):
    # Filtra las tareas que corresponden a los informes creados por el usuario actual
    tareas = Tarea.objects.filter(informe__user=request.user)
    return render(request, 'tareas/lista_tareas_operarios_supervisores.html', {'tareas': tareas})


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Técnicos', 'Externos']).exists())
def lista_tareas_tecnicos(request):
    # Filtra las tareas que están asignadas al técnico actual
    tareas = Tarea.objects.filter(tecnico=request.user)
    return render(request, 'tareas/lista_tareas_tecnicos.html', {'tareas': tareas})


@login_required
@user_passes_test(lambda u: u.groups.filter(name__in=['Administradores', 'Supervisores']).exists())
def detalle_informe_reporte_feedback(request, tarea_id):
    # Recupera la tarea específica y sus relaciones
    tarea = Tarea.objects.select_related('informe').prefetch_related('feedback').get(id=tarea_id)
    try:
        reporte = tarea.reporte
    except Tarea.reporte.RelatedObjectDoesNotExist:
        reporte = None
    try:
        feedback = tarea.feedback
    except Tarea.feedback.RelatedObjectDoesNotExist:
        feedback = None
    return render(request, 'tareas/detalle_informe_reporte_feedback.html', {
        'tarea': tarea,
        'informe': tarea.informe,
        'reporte': reporte,
        'feedback': feedback
    })



