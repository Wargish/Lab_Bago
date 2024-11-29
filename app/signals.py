from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from .models import Estado, Notificacion, SolicitudExterno, PresupuestoExterno
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
        estados = ['Pendiente', 'En Curso', 'Completada', 'Archivada', 'Rechazada']
        for nombre in estados:
            Estado.objects.get_or_create(nombre=nombre)


# Signal para enviar correo de manera asíncrona cuando se crea una Notificación
@receiver(post_save, sender=Notificacion)
def enviar_correo_asincrono_notificacion(sender, instance, created, **kwargs):
    if created:
        print(f"Notificación creada: {instance}")
        threading.Thread(target=send_correo_notificacion, args=(instance,)).start()


def send_correo_notificacion(notificacion):
    asunto = f"Notificación de Informe: {notificacion.informe.objetivo}"
    texto_plano = f"""
    Hola {notificacion.usuario.username},

    Se te ha asignado una nueva tarea. A continuación, te presentamos algunos detalles del informe:

    Objetivo del Informe: {notificacion.informe.objetivo}
    Categoría: {'Infraestructura' if notificacion.informe.categoría == 'INF' else 'Maquinaria'}
    Ubicación: {notificacion.informe.ubicacion.nombre if notificacion.informe.ubicacion else 'No especificada'}
    Fecha de Creación del Informe: {notificacion.informe.creado_en.strftime('%d/%m/%Y %H:%M:%S')}
    
    Puedes acceder al informe a través de tu panel de Tareas.

    ¡Saludos!
    """
    html_contenido = f"""
    <p>Hola <strong>{notificacion.usuario.username}</strong>,</p>
    <p>Se te ha asignado una nueva tarea. A continuación, te presentamos algunos detalles del informe:</p>
    <ul>
        <li><strong>Objetivo del Informe:</strong> {notificacion.informe.objetivo}</li>
        <li><strong>Categoría:</strong> {"Infraestructura" if notificacion.informe.categoría == "INF" else "Maquinaria"}</li>
        <li><strong>Ubicación:</strong> {notificacion.informe.ubicacion.nombre if notificacion.informe.ubicacion else "No especificada"}</li>
        <li><strong>Fecha de Creación del Informe:</strong> {notificacion.informe.creado_en.strftime('%d/%m/%Y %H:%M:%S')}</li>
    </ul>
    <p>Puedes acceder al informe a través de tu panel de Tareas.</p>
    <p>¡Saludos!</p>
    """

    destinatarios = [notificacion.usuario.email]

    try:
        mensaje = EmailMultiAlternatives(asunto, texto_plano, settings.DEFAULT_FROM_EMAIL, destinatarios)
        mensaje.attach_alternative(html_contenido, "text/html")
        mensaje.send()
        print(f"Correo enviado a {destinatarios}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")


# Signal para enviar correo de manera asíncrona cuando se crea una SolicitudExterno
@receiver(post_save, sender=SolicitudExterno)
def enviar_correo_asincrono_solicitud(sender, instance, created, **kwargs):
    if created:
        print(f"Solicitud de externo creada: {instance}")
        threading.Thread(target=send_correo_solicitud, args=(instance,)).start()


def send_correo_solicitud(solicitud):
    asunto = "Nueva Solicitud de Trabajo"
    texto_plano = f"""
    Estimado {solicitud.nombre_externo},

    Se ha generado una nueva solicitud de trabajo para usted. A continuación, los detalles:

    - Fecha del trabajo: {solicitud.fecha_creacion.strftime('%d/%m/%Y')}
    - Descripción: {solicitud.descripcion}

    Por favor, revise el archivo adjunto para más información.

    Saludos,
    Equipo de Mantenimiento
    """
    html_contenido = f"""
    <p>Estimado <strong>{solicitud.nombre_externo}</strong>,</p>
    <p>Se ha generado una nueva solicitud de trabajo para usted. A continuación, los detalles:</p>
    <ul>
        <li><strong>Fecha de Solicitud:</strong> {solicitud.fecha_creacion.strftime('%d/%m/%Y')}</li>
        <li><strong>Descripción:</strong> {solicitud.descripcion}</li>
    </ul>
    <p>Por favor, revise el archivo adjunto para más información.</p>
    <p>Saludos,</p>
    <p><strong>Equipo de Mantenimiento</strong></p>
    """

    destinatarios = [solicitud.correo_externo]

    try:
        mensaje = EmailMultiAlternatives(asunto, texto_plano, settings.DEFAULT_FROM_EMAIL, destinatarios)
        # Adjuntar el PDF si está presente
        if solicitud.pdf_peticion:
            mensaje.attach(solicitud.pdf_peticion.name, solicitud.pdf_peticion.read(), 'application/pdf')

        mensaje.attach_alternative(html_contenido, "text/html")
        mensaje.send()
        print(f"Correo enviado a {destinatarios}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")




@receiver(post_save, sender=PresupuestoExterno)
def enviar_correo_asincrono_presupuesto(sender, instance, created, **kwargs):
    if instance.aprobado and instance.fecha_asistencia:
        threading.Thread(target=enviar_correo_externo, args=(instance,)).start()

def enviar_correo_externo(presupuesto):
    asunto = f"Trabajo Aprobado - Fecha de Asistencia Asignada"
    texto_plano = f"""
    Hola {presupuesto.solicitud.nombre_externo},

    Tu presupuesto ha sido aprobado. Por favor, revisa la fecha de asistencia asignada:

    Fecha de Asistencia: {presupuesto.fecha_asistencia.strftime('%d/%m/%Y')}

    ¡Gracias por tu colaboración!
    """
    html_contenido = f"""
    <p>Hola <strong>{presupuesto.solicitud.nombre_externo}</strong>,</p>
    <p>Tu presupuesto ha sido aprobado. Por favor, revisa la fecha de asistencia asignada:</p>
    <ul>
        <li><strong>Fecha de Asistencia:</strong> {presupuesto.fecha_asistencia.strftime('%d/%m/%Y')}</li>
    </ul>
    <p>¡Gracias por tu colaboración!</p>
    """

    destinatarios = [presupuesto.solicitud.correo_externo]
    try:
        mensaje = EmailMultiAlternatives(asunto, texto_plano, settings.DEFAULT_FROM_EMAIL, destinatarios)
        mensaje.attach_alternative(html_contenido, "text/html")
        mensaje.send()
        print(f"Correo enviado a {destinatarios}")
    except Exception as e:
        print(f"Error al enviar correo: {e}")
