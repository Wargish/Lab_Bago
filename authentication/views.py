from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404

from authentication.forms import RegistroForm, LoginForm
from internal_workers.models import Tarea
import sweetify

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


def roles(request):
    try:
        # Código de la vista
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
                username = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')
                usuario.username = username
                usuario.email = email
                if password:
                    usuario.set_password(password)
                usuario.save()
            elif action == 'assign_task':
                tarea_id = request.POST.get('task_id')
                tarea = get_object_or_404(Tarea, id=tarea_id)
                tarea.asignar_tecnico(usuario)
    except Exception as e:
        print(f"Error en la vista roles: {e}")
        raise
    
    role_filter = request.GET.get('role', 'all')

    usuarios = User.objects.all()

    if role_filter != 'all':
        usuarios = usuarios.filter(groups__name=role_filter)

    roles = Group.objects.all()
    tareas_sin_tecnico = Tarea.objects.filter(asignado_a__isnull=True)

    return render(request, "roles.html", {'usuarios': usuarios, 'roles': roles, 'tareas_sin_tecnico': tareas_sin_tecnico})

def cerrar_session(request):
    logout(request)
    sweetify.sweetalert(request, icon='success', title='Sesión cerrada', text='Has cerrado sesión exitosamente.')
    return redirect('home')
