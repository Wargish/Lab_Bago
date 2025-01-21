from django.db.models.signals import post_migrate, post_save
from django.contrib.auth.models import Group, User
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives, send_mail
from django.conf import settings
from internal_workers.models import Tarea, Notificacion, Estado
from external_workers.models import SolicitudExterno, PresupuestoExterno
import os
import threading
import time

@receiver(post_migrate)
def create_superuser(sender, **kwargs):
    username = 'PatricioDiaz'
    email = 'Pat.moralesg@gmail.com'
    password = '123456789'
    
    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f'Superuser {username} created successfully.')
    else:
        print(f'Superuser {username} already exists.')

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
        print('Grupos y estados creados exitosamente.')
    else:
        print('No se crearon grupos ni estados.')

@receiver(post_save, sender=SolicitudExterno)
def enviar_correo_asincrono_solicitud(sender, instance, created, **kwargs):
    if created:
        def send_delayed():
            # Esperar a que el archivo esté guardado
            time.sleep(5)
            # Recargar la instancia para obtener el archivo actualizado
            instance.refresh_from_db()
            send_correo_solicitud(instance)
            
        threading.Thread(target=send_delayed).start()

def send_correo_solicitud(solicitud):
    print(f"Iniciando envío de correo para solicitud {solicitud.id}")    
    asunto = "Nueva Solicitud de Trabajo"
    texto_plano = f"""
    Estimado {solicitud.externo.username},  

    Se ha generado una nueva solicitud de trabajo para usted. A continuación, los detalles:

    - Fecha de Creacion: {solicitud.fecha_creacion.strftime('%d/%m/%Y')}
    - Descripción: {solicitud.descripcion}

    Por favor, revise el archivo adjunto para más información.

    Saludos,
    Equipo de Mantenimiento
    """
    html_contenido = f"""
    <p>Estimado <strong>{solicitud.externo.username}</strong>,</p>
    <p>Se ha generado una nueva solicitud de trabajo para usted. A continuación, los detalles:</p>
    <ul>
        <li><strong>Fecha de Solicitud:</strong> {solicitud.fecha_creacion.strftime('%d/%m/%Y')}</li>
        <li><strong>Descripción:</strong> {solicitud.descripcion}</li>
    </ul>
    <p>Por favor, revise el archivo adjunto para más información.</p>
    <p>Saludos,</p>
    <p><strong>Sistema de Servicios Generales</strong></p>
    """

    destinatarios = [solicitud.externo.email]

    try:
        mensaje = EmailMultiAlternatives(asunto, texto_plano, settings.DEFAULT_FROM_EMAIL, destinatarios)

        # Adjuntar el PDF si está presente
        if solicitud.pdf_peticion and hasattr(solicitud.pdf_peticion, 'file'):
            try:
                pdf_content = solicitud.pdf_peticion.read()
                pdf_name = os.path.basename(solicitud.pdf_peticion.name)
                mensaje.attach(pdf_name, pdf_content, 'application/pdf')
            except Exception as e:
                print(f"Error al leer el PDF: {e}")
            finally:
                solicitud.pdf_peticion.close()

        mensaje.attach_alternative(html_contenido, "text/html")
        mensaje.send()
        print(f"Correo enviado exitosamente a {destinatarios}")
        
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        print(f"Detalles adicionales: {str(e)}")

# signal para enviar correo sobre el estado del presupuesto
@receiver(post_save, sender=PresupuestoExterno)
def enviar_correo_presupuesto(sender, instance, created, **kwargs):
    solicitud = instance.tarea_externo.solicitud
    externo_email = solicitud.externo.email
    asunto = ''
    mensaje = ''

    if instance.estado == 'rechazado':
        asunto = 'Presupuesto Rechazado'
        mensaje = f"""
        Hola {solicitud.externo.username},

        Lamentamos informarte que el presupuesto enviado ha sido rechazado.
        Razón del rechazo: {instance.mensaje}

        Gracias por tu comprensión.
        Sistema de Servicios Generales
        """
    elif instance.estado == 'aprobado':
        asunto = 'Presupuesto Aprobado'
        mensaje = f"""
        Hola {solicitud.externo.username},

        Nos complace informarte que tu presupuesto ha sido aprobado.
        Fecha de asistencia asignada: {instance.fecha_asistencia.strftime('%d/%m/%Y')}

        ¡Gracias por tu colaboración!
        Sistema de Servicios Generales
        """

    if asunto and mensaje:
        send_mail(
            asunto,
            mensaje,
            settings.DEFAULT_FROM_EMAIL,
            [externo_email],
            fail_silently=False,
        )



@receiver(post_save, sender=Tarea)
def tarea_rechazada(sender, instance, **kwargs):
    # Check if state changed to Rechazada
    if instance.estado and instance.estado.nombre == 'Rechazada':
        # Get all superusers
        superusers = User.objects.filter(is_superuser=True)
        
        # Create notification for each superuser
        for admin in superusers:
            Notificacion.objects.create(
                usuario=admin,
                informe=instance.informe,
                mensaje=f'La tarea "{instance.objetivo}" ha sido rechazada. Por favor, revise los detalles.'
            )
            
            # Send email
            send_mail(
                'Notificación de Tarea Rechazada',
                f'''Estimado {admin.username},

                Le informamos que una tarea ha sido rechazada. A continuación, los detalles:

                - Objetivo de la Tarea: {instance.objetivo}
                - Informe Asociado: {instance.informe.objetivo}
                - Técnico Asignado: {instance.asignado_a.username if instance.asignado_a else "No asignado"}
                - Fecha de Creación: {instance.creado_en.strftime('%d-%m-%Y %H:%M')}

                Por favor, revise el sistema para más detalles.

                Saludos,
                Sistema de Servicios Generales
                ''',
                settings.DEFAULT_FROM_EMAIL,
                [admin.email],
                fail_silently=False,
            )