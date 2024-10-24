from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from  django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import *

def base(request):
    return render(request, "app/base.html")

def home(request):
    return render(request, "app/home.html")

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

def login(request):
    form = LoginForm()
    return render(request, "app/auth/login.html", {'form': form})

def logout(request):
    logout(request)
    return redirect('home')

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')  # Redirige a la página de inicio de sesión
    else:
        form = RegistroForm()
    return render(request, 'app/auth/registro.html', {'form': form})

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
    return render(request, "app/infraestructura/informe.html", {'form': form})

def reporte(request):
    return render(request, "app/infraestructura/reporte.html")

def graficos(request):
    return render(request, "app/dashboard/graficos.html")