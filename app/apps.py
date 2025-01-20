from django.apps import AppConfig
import os

class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'

    def ready(self):
        # Importa los signals (si ya tienes señales configuradas)
        from . import signals

        # Lógica para crear el superusuario automáticamente
        if os.environ.get('RUN_MAIN', None) != 'true':
            return  # Evitar que se ejecute más de una vez en algunos servidores

        from django.contrib.auth.models import User

        SUPERUSER_USERNAME = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
        SUPERUSER_EMAIL = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        SUPERUSER_PASSWORD = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

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