from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Estado, Notificacion
import threading

# Signal para crear grupos y estados después de las migraciones
@receiver(post_migrate)
def create_groups(sender, **kwargs):
    if sender.name == 'app':  # Cambia 'app' por el nombre correcto de tu módulo
        Group.objects.get_or_create(name='Operario')
        Group.objects.get_or_create(name='Técnico')
        Group.objects.get_or_create(name='Externo')
        Group.objects.get_or_create(name='Supervisor')

        # Crear estados para las tareas
        estados = ['Pendiente', 'En Curso', 'Completada', 'Archivar', 'Rechazada']
        for nombre in estados:
            Estado.objects.get_or_create(nombre=nombre)

# Signal para enviar correo de manera asíncrona cuando se crea una Notificacion
@receiver(post_save, sender=Notificacion)
def enviar_correo_asincrono(sender, instance, created, **kwargs):
    if created:
        # Usar threading para ejecutar el envío del correo en segundo plano
        threading.Thread(target=send_correo, args=(instance,)).start()

def send_correo(notificacion):
    asunto = f"Notificación de Informe: {notificacion.informe.objetivo}"
    mensaje = f"""
    Hola {notificacion.usuario.username},

    Se te ha asignado una nueva tarea. A continuación, te presentamos algunos detalles del informe:

    **Objetivo del Informe**: {notificacion.informe.objetivo}
    **Tipo de Informe**: {'Infraestructura' if notificacion.informe.tipo_informe == 'INF' else 'Maquinaria'}
    **Ubicación**: {notificacion.informe.ubicacion.nombre if notificacion.informe.ubicacion else 'No especificada'}
    **Fecha de Creación del Informe**: {notificacion.informe.creado_en.strftime('%d/%m/%Y %H:%M:%S')}
    
    Puedes acceder al informe a través de tu panel de Tareas.

    ¡Saludos!
    """
    
    destinatarios = [notificacion.usuario.email]
    
    try:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            destinatarios,
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error al enviar correo: {e}")

