from django.db import models
from django.contrib.auth.models import User, Group


def create_groups():
    Group.objects.get_or_create(name='Operarios')
    Group.objects.get_or_create(name='Técnicos')

class Lugar(models.Model):
    nombre = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre

class Estado(models.Model):
    nombre = models.CharField(max_length=100)

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
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, default=None)
    image = models.ImageField(upload_to='app/static/images/')
    tipo_Informe = models.CharField(max_length=3, choices=TIPO_REPORTE_CHOICES, default=INFRASTRUCTURA)

    def save(self, *args, **kwargs):
        if not self.estado:
            estado_pendiente = Estado.objects.filter(nombre='Pendiente').first()
            if estado_pendiente:
                self.estado = estado_pendiente
        super().save(*args, **kwargs)
        self.generar_notificaciones()

    def generar_notificaciones(self):
        tecnicos = Group.objects.get(name='Técnicos').user_set.all()
        for tecnico in tecnicos:
            Notificacion.objects.create(
                user=tecnico,
                mensaje=self
            )

    def __str__(self):
        return f'Informe: {self.objetivo}'

    
class Notificacion(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.ForeignKey(InformeCondiciones, on_delete=models.CASCADE)
    leido = models.BooleanField(default=False)
    createdAt = models.DateTimeField(auto_now_add=True)

    def marcar_como_leido(self):
        self.leido = True
        self.save()

    def __str__(self):
        return f'Notificación para {self.user.username}: {self.mensaje.objetivo}'
    

class Reporte(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    lugar = models.ForeignKey(Lugar, on_delete=models.SET_NULL, null=True)
    objetivo = models.TextField(null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)
    image = models.ImageField(upload_to='app/static/images/')

    def __str__(self):
        return f'Reporte: {self.objetivo}'