from django.db import models
from django.contrib.auth.models import User

class Ubicacion(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Estado(models.Model):
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre

class Informe(models.Model):
    INFRAESTRUCTURA = 'INF'
    MAQUINARIA = 'MAQ'
    CATEGORIA_CHOICES = [
        (INFRAESTRUCTURA, 'Infraestructura'),
        (MAQUINARIA, 'Maquinaria'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="informes")
    creado_en = models.DateTimeField(auto_now_add=True)
    ubicacion = models.ForeignKey(Ubicacion, on_delete=models.SET_NULL, null=True)
    objetivo = models.TextField(null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to='informes/')
    categoría = models.CharField(max_length=3, choices=CATEGORIA_CHOICES, default=INFRAESTRUCTURA)

    class Meta:
        ordering = ['-creado_en']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Tarea.objects.filter(informe=self).exists():
            Tarea.objects.create(informe=self, objetivo=self.objetivo)

    def __str__(self):
        return f'Informe: {self.objetivo}'

from django.core.mail import send_mail
from django.conf import settings

class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    informe = models.ForeignKey(Informe, on_delete=models.CASCADE)
    leido = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    mensaje = models.TextField(null=True, blank=True)

    def marcar_como_leido(self):
        self.leido = True
        self.save()

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class Tarea(models.Model):
    informe = models.ForeignKey(Informe, on_delete=models.CASCADE)
    objetivo = models.TextField(null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, blank=True)
    asignado_a = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="tareas")
    creado_en = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.estado:
            self.estado = Estado.objects.get(nombre='Pendiente')
        self.objetivo = self.informe.objetivo
        super().save(*args, **kwargs)

    def asignar_tecnico(self, tecnico):
        if self.asignado_a:
            # Notificar al técnico anterior que la tarea fue reasignada
            Notificacion.objects.create(usuario=self.asignado_a, informe=self.informe, mensaje=f'Tarea reasignada: {self.objetivo}')
        
        self.asignado_a = tecnico
        self.save()
        Notificacion.objects.create(usuario=tecnico, informe=self.informe, mensaje=f'Tarea asignada: {self.objetivo}')

    def __str__(self):
        return f'Tarea: {self.objetivo} - Estado: {self.estado}'

class ReporteTarea(models.Model):
    tarea = models.OneToOneField(Tarea, on_delete=models.CASCADE, related_name='reporte_tarea')
    contenido = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to='reportes_tarea/', blank=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        self.tarea.estado = Estado.objects.get(nombre='Completada')
        self.tarea.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Reporte de Tarea: {self.tarea.objetivo} - Fecha: {self.creado_en.strftime("%Y-%m-%d %H:%M")}'

class FeedbackTarea(models.Model):
    tarea = models.OneToOneField(Tarea, on_delete=models.CASCADE)
    aprobado = models.BooleanField()
    comentarios = models.TextField(null=True, blank=True)
    creado_en = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.aprobado:
            self.tarea.estado = Estado.objects.get(nombre='Rechazada')
        else:
            self.tarea.estado = Estado.objects.get(nombre='Archivada')
        self.tarea.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Feedback para Tarea: {self.tarea.objetivo} - Aprobado: {"Sí" if self.aprobado else "No"}'
    

# Externos

class SolicitudExterno(models.Model):
    externo = models.ForeignKey(User, on_delete=models.CASCADE, related_name='solicitudes_externas')
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    objetivo = models.CharField(max_length=200)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='ex_peticiones_imagenes/', blank=True, null=True)
    pdf_peticion = models.FileField(upload_to='ex_peticiones/', blank=True, null=True)
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
    archivo = models.FileField(upload_to='ex_presupuestos/')
    fecha_asistencia = models.DateField(null=True, blank=True)
    estado = models.CharField(
        max_length=20,
        choices=[('pendiente', 'Pendiente'), ('aprobado', 'Aprobado'), ('rechazado', 'Rechazado')],
        default='pendiente'
    )
    mensaje = models.TextField(blank=True, null=True)
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
    descripcion = models.TextField(blank=True, null=True)
    imagen = models.ImageField(upload_to='ex_reporte_imagenes/', blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)


    def __str__(self):
        return f"Reporte de {self.tarea_externo.solicitud.externo.username} - {self.fecha_creacion}"

class ExternoFeedback(models.Model):
    tarea_externo = models.OneToOneField(TareaExterno, on_delete=models.CASCADE, related_name='externo_feedback')
    aprobado = models.BooleanField()
    comentario = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    creado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        nuevo_estado = 'completada' if self.aprobado else 'rechazada'
        self.tarea_externo.actualizar_estado(nuevo_estado)

    def __str__(self):
        return f"Feedback de {self.creado_por.username} - {self.fecha_creacion}"
    