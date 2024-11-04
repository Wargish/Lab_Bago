from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *

#FILTRO DE GRUPOS
def group_required(*group_names):
    def in_groups(u):
        return u.is_authenticated and bool(u.groups.filter(name__in=group_names))
    return user_passes_test(in_groups)


# VISTAS BASICAS

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


@login_required
@user_passes_test(lambda u: u.is_superuser)
def roles(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        rol = request.POST.get('rol')
        usuario = get_object_or_404(User, id=usuario_id)
        
        grupo = Group.objects.get(name=rol)
        grupo.user_set.add(usuario)
    
    usuarios = User.objects.all()
    roles = Group.objects.all()

    return render(request, "app/auth/roles.html",{'usuarios': usuarios, 'roles': roles})

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



#VISTAS RENDER, CRUD Y MOVIMIENTO DE INFORMACION
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
def notificaciones(request):
    notificaciones = Notificacion.objects.filter(user=request.user)
    return render(request, "app/notificaciones.html", {'notificaciones': notificaciones})

@login_required
def notificaciones_id(request, notificaciones_id):
    notificacion = Notificacion.objects.get(id=notificaciones_id)
    return render(request, "app/notificaciones_id.html", {'notificacion': notificacion})

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
    tareas = Tarea.objects.none()  # Inicializa con un QuerySet vacío

    # Filtra las tareas según el grupo del usuario
    if request.user.groups.filter(name='Técnico').exists() or request.user.groups.filter(name='Externo').exists():
        if estado_selec == 'todos':
            tareas = Tarea.objects.filter(tecnico=request.user)
        elif estado_selec in estados_validos:
            tareas = Tarea.objects.filter(tecnico=request.user, estado__nombre=estado_selec)
    elif request.user.groups.filter(name='Supervisor').exists() or request.user.groups.filter(name='Operario').exists():
        if estado_selec == 'todos':
            tareas = Tarea.objects.filter(informe__user=request.user)
        elif estado_selec in estados_validos:
            tareas = Tarea.objects.filter(informe__user=request.user, estado__nombre=estado_selec)

    es_superusuario = request.user.is_superuser
    es_tecnico = request.user.groups.filter(name='Técnico').exists()
    es_externo = request.user.groups.filter(name='Externo').exists()
    es_supervisor = request.user.groups.filter(name='Supervisor').exists()
    es_operario = request.user.groups.filter(name='Operario').exists()

    return render(request, "app/dashboard/listar_tareas.html", {
        'tareas': tareas,
        'estado_selec': estado_selec,
        'es_superusuario': es_superusuario,
        'es_tecnico': es_tecnico,
        'es_externo': es_externo,
        'es_supervisor': es_supervisor,
        'es_operario': es_operario,
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





#METODOS PERSONALIZADAS

@login_required
def marcar_notificacion_como_leida(request, notificacion_id):
    notificacion = Notificacion.objects.get(id=notificacion_id)
    if notificacion.user == request.user:
        notificacion.marcar_como_leido()

@login_required
def detalle_informe(request, informe_id):
    informe = get_object_or_404(InformeCondiciones, id=informe_id)
    return render(request, 'app/detalle_informe.html', {'informe': informe})

@login_required
def detalle_reporte(request, reporte_id):
    reporte = get_object_or_404(Reporte, id=reporte_id)
    return render(request, 'app/detalle_reporte.html', {'reporte': reporte})

@login_required
def detalle_feedback(request, feedback_id):
    feedback = get_object_or_404(Feedback, id=feedback_id)
    return render(request, 'app/detalle_feedback.html', {'feedback': feedback})
