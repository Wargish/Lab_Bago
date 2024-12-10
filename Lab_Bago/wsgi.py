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