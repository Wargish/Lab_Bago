from django.db import models
from django.contrib.auth.models import User


# Externos

class SolicitudExterno(models.Model):
    externo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_externas')
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    objetivo = models.CharField(max_length=200, null=False, blank=False)
    descripcion = models.TextField(null=False, blank=False)
    imagen = models.ImageField(upload_to='ex_peticiones_imagenes/', null=False, blank=False)
    pdf_peticion = models.FileField(upload_to='ex_peticiones/', null=False, blank=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            TareaExterno.objects.create(solicitud=self)

    def __str__(self):
        return f"Solicitud a {self.externo.username} - {self.fecha_creacion}"

class TareaExterno(models.Model):
    solicitud = models.ForeignKey(SolicitudExterno, on_delete=models.CASCADE, related_name='tareas_externas')
    estado = models.CharField(
        max_length=20,
        choices=[('en_espera', 'En Espera'), ('en_curso', 'En Curso'), ('completada', 'Completada'), ('rechazada', 'Rechazada')],
        default='en_espera'
    )
    fecha_asistencia = models.DateField(null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def actualizar_estado(self, nuevo_estado):
        self.estado = nuevo_estado
        self.save()

    def __str__(self):
        return f"Tarea de {self.solicitud.externo.username} - {self.estado}"

class PresupuestoExterno(models.Model):
    tarea_externo = models.OneToOneField(TareaExterno, on_delete=models.CASCADE, related_name='presupuesto_externo')
    archivo = models.FileField(upload_to='ex_presupuestos/', blank=False)
    fecha_asistencia = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )
    mensaje = models.TextField(blank=False, null=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.fecha_asistencia:
            self.tarea_externo.fecha_asistencia = self.fecha_asistencia
            self.tarea_externo.save()
        self.tarea_externo.actualizar_estado('en_curso')

    def __str__(self):
        return f"Presupuesto de {self.tarea_externo.solicitud.externo.username} - Estado: {self.estado}"

class ExternoReporte(models.Model):
    tarea_externo = models.OneToOneField(TareaExterno, on_delete=models.CASCADE, related_name='externo_reportes')
    descripcion = models.TextField(blank=False, null=True)
    imagen = models.ImageField(upload_to='ex_reporte_imagenes/', blank=False, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"Reporte de {self.tarea_externo.solicitud.externo.username} - {self.fecha_creacion}"

class ExternoFeedback(models.Model):
    tarea_externo = models.OneToOneField(TareaExterno, on_delete=models.CASCADE, related_name='externo_feedback')
    aprobado = models.BooleanField(blank=False)
    comentario = models.TextField(null=False, blank=True, default="Trabajo aprobado")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        nuevo_estado = 'completada' if self.aprobado else 'rechazada'
        self.tarea_externo.actualizar_estado(nuevo_estado)

    def __str__(self):
        return f"Feedback de {self.creado_por.username} - {self.fecha_creacion}"
    

