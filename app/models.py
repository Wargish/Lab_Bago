from django.db import models
from django.contrib.auth.models import User, Group


def create_groups():
    Group.objects.get_or_create(name='Operarios')
    Group.objects.get_or_create(name='Técnicos')

class Lugar(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre
    
class InformeCondiciones(models.Model):
    INFRASTRUCTURA = 'INF'
    MAQUINARIA = 'MAQ'
    TIPO_REPORTE_CHOICES = [
        (INFRASTRUCTURA, 'Infraestructura'),
        (MAQUINARIA, 'Maquinaria'),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    _id = models.AutoField(primary_key=True, editable=False)  
    createdAt = models.DateTimeField(auto_now_add=True)
    lugar = models.ForeignKey(Lugar, on_delete=models.SET_NULL, null=True)
    objetivo = models.TextField(null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='app/static/images/', blank=False)
    tipo_Informe = models.CharField(max_length=3, choices=TIPO_REPORTE_CHOICES, default=INFRASTRUCTURA)

    class meta():
        ordering = ['-createdAt']

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        Notificacion.crear_notificaciones(self)
        Tarea.objects.create(informe=self, objetivo=self.objetivo)


    def __str__(self):
        return f'Informe: {self.objetivo}'

    
class Notificacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Informe = models.ForeignKey(InformeCondiciones, on_delete=models.CASCADE)
    leido = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    @classmethod
    def crear_notificaciones(cls, informe):
        tecnicos = Group.objects.get(name='Técnicos').user_set.all()
        for tecnico in tecnicos:
            cls.objects.create(user=tecnico, mensaje=informe)

    def marcar_como_leido(self):
        self.leido = True
        self.save()

    def __str__(self):
        return f'Notificación para {self.user.username}: {self.mensaje.objetivo}'
    

class Tarea(models.Model):
    informe = models.ForeignKey(InformeCondiciones, on_delete=models.CASCADE)
    objetivo = models.TextField(null=True, blank=True)
    estado = models.CharField(max_length=20,
                              choices= [
                                    ('Pendiente', 'Pendiente'),
                                    ('En Curso', 'En Curso'),
                                    ('Completada', 'Completada'),
                                    ('Archivar', 'Archivar'),
                                    ],
                                    default='Pendiente'
                            )
    tecnico = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    createdAt = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.objetivo = self.informe.objetivo
        super().save(*args, **kwargs)

    def aceptar(self, tecnico):
        self.tecnico = tecnico
        self.estado = 'En Curso'
        self.save()

    def marcar_como_completada(self):
        self.estado = 'Completada'
        self.save()

    def archivada(self):
        self.estado = 'Archivar'
        self.save()

    def __str__(self):
        return f'Tarea: {self.objetivo} - Estado: {self.estado}'
    

class Reporte(models.Model):
    tarea = models.ForeignKey(Tarea, on_delete=models.CASCADE)
    contenido = models.TextField(null=True, blank=True)
    imagen = models.ImageField(upload_to='app/static/images/', blank=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Reporte de Tarea: {self.tarea.objetivo} - Fecha: {self.createdAt.strftime("%Y-%m %H:%M")}'

    

