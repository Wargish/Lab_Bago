# Importaciones estándar de Django
from django.shortcuts import render, redirect, get_object_or_404,HttpResponseRedirect
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render
# Importaciones locales (formularios y modelos)
from .forms import *
from .models import *
import sweetify


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
            sweetify.sweetalert(request, icon='success', persistent='Ok', title='Registro exitoso', text='Usuario creado correctamente')
            return redirect('home')
        else:
            sweetify.error(request, 'Error', text='Error en el formulario.', persistent='Ok')
    else:
        form = RegistroForm()
    return render(request, "auth/registro.html", {'form': form})

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
        form = LoginForm()
    return render(request, "auth/login.html", {'form': form})

def cerrar_session(request):
    logout(request)
    return redirect('home')
