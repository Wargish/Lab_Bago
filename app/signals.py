from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group
from django.dispatch import receiver
from .models import Estado

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.name == 'app':  # Cambia 'app' por el nombre correcto de tu módulo
        Group.objects.get_or_create(name='Operario')
        Group.objects.get_or_create(name='Técnico')
        Group.objects.get_or_create(name='Externo')
        Group.objects.get_or_create(name='Supervisor')

        # Crear estados
        estados = ['Pendiente', 'En Curso', 'Completada', 'Archivar', 'Rechazada']
        for nombre in estados:
            Estado.objects.get_or_create(nombre=nombre)