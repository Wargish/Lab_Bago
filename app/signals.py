from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver
from .models import Estado

@receiver(post_migrate)
def setup_initial_data(sender, **kwargs):
    if sender.name == 'app':
        # Crear grupos
        for group_name in ['Administrador', 'Operario', 'Técnico', 'Externo', 'Supervisor']:
            Group.objects.get_or_create(name=group_name)

        # Crear estados
        estados = ['Pendiente', 'En Curso', 'Completada', 'Archivar', 'Rechazada']
        for nombre in estados:
            Estado.objects.get_or_create(nombre=nombre)