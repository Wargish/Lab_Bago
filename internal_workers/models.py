from django.db import models
from django.contrib.auth.models import User

class Zona(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre
    
class UbicacionTecnica(models.Model):
    zona = models.ForeignKey(Zona, related_name='ubicaciones_tecnicas', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.codigo} ({self.descripcion})"

class Equipo(models.Model):
    ubicacion_tecnica = models.ForeignKey(UbicacionTecnica, related_name='equipos', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=255)
    descripcion = models.TextField(null=True, blank=True)


    def __str__(self):
        return f"{self.codigo} ({self.descripcion})"


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
    zona = models.ForeignKey(Zona, on_delete=models.SET_NULL, null=True)
    objetivo = models.TextField(null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to='informes/')
    categoría = models.CharField(max_length=3, choices=CATEGORIA_CHOICES, default=INFRAESTRUCTURA)
    ubicacion_tecnica = models.ForeignKey(UbicacionTecnica, on_delete=models.SET_NULL, null=True, blank=True)
    equipo = models.ForeignKey(Equipo, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-creado_en']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not Tarea.objects.filter(informe=self).exists():
            Tarea.objects.create(informe=self, objetivo=self.objetivo)

    def __str__(self):
        return f'Informe: {self.objetivo}'

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
        Notificacion.objects.create(
            usuario=self.tarea.informe.usuario,
            informe=self.tarea.informe,
            mensaje=f'Se ha creado un reporte para la tarea: {self.tarea.objetivo}'
        )

    def __str__(self):
        return f'Reporte de Tarea: {self.tarea.objetivo} - Fecha: {self.creado_en.strftime("%Y-%m-%d %H:%M")}'

class FeedbackTarea(models.Model):
    tarea = models.OneToOneField(Tarea, on_delete=models.CASCADE)
    aprobado = models.BooleanField()
    comentarios = models.TextField(null=False, blank=True, default="Trabajo aprobado")
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