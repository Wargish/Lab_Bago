from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
import sweetify
from .forms import *
from .models import *

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
    return render(request, "registro.html", {'form': form})



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
    return render(request, "login.html", {'form': form})



def cerrar_session(request):
    logout(request)
    sweetify.sweetalert(request, icon='success', title='Sesión cerrada', text='Has cerrado sesión exitosamente.')
    return redirect('home')

