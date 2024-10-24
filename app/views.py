from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import *

def base(request):
    return render(request, "app/base.html")

def home(request):
    return render(request, "app/home.html")

@user_passes_test(lambda u: u.is_superuser)
def admin(request):
    if request.method == 'POST':
        usuario_id = request.POST.get('usuario_id')
        rol = request.POST.get('rol')
        usuario = get_object_or_404(User, id=usuario_id)
        
        # Asignar el rol
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
    return render(request, "app/infraestructura/reporte.html")

@login_required
def graficos(request):
    return render(request, "app/dashboard/graficos.html")

@login_required
def notificaciones(request):
    notificaciones = Notificacion.objects.filter(user=request.user, leido=False)
    context = {
        'notificaciones': notificaciones,
    }
    return render(request, 'app/base.html', context)

@login_required
def marcar_notificacion_como_leida(request, notificacion_id):
    notificacion = Notificacion.objects.get(id=notificacion_id)
    if notificacion.user == request.user:
        notificacion.marcar_como_leido()
    return redirect('nombre_de_la_vista_donde_redirigir')