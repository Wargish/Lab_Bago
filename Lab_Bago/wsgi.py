import os
import sys

# Ajusta esta ruta al directorio donde está tu proyecto Django (el directorio raíz)
project_home = '/home/Pmorales/Lab_Bago'  # Cambia esta ruta si es necesario
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Configura la variable de entorno para Django, apuntando al archivo 'settings.py' dentro de 'Lab_Bago'
os.environ['DJANGO_SETTINGS_MODULE'] = 'Lab_Bago.settings'  # Apunta correctamente a settings.py dentro de Lab_Bago/

# Cargar la aplicación WSGI de Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Crear superusuario automáticamente si no existe
from django.contrib.auth.models import User

# Configura aquí las credenciales del superusuario
SUPERUSER_USERNAME = 'PatricioDiaz'  # Cambia este nombre de usuario
SUPERUSER_EMAIL = 'bago.emailtest@gmail.com'  # Cambia este correo electrónico
SUPERUSER_PASSWORD = '123456789'  # Cambia esta contraseña (usa variables de entorno en producción)

try:
    if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
        User.objects.create_superuser(
            username=SUPERUSER_USERNAME,
            email=SUPERUSER_EMAIL,
            password=SUPERUSER_PASSWORD,
        )
        print(f'Superusuario creado automáticamente: {SUPERUSER_USERNAME}')
    else:
        print('El superusuario ya existe')
except Exception as e:
    print(f'Error al crear el superusuario automáticamente: {e}')
