from django.db import models
from django.contrib.auth.models import User, Group

def create_groups():
    Group.objects.get_or_create(name='Administradores')
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

class Informe(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    _id = models.AutoField(primary_key=True, editable=False)  
    createdAt = models.DateTimeField(auto_now_add=True)
    lugar = models.ForeignKey(Lugar, on_delete=models.SET_NULL, null=True)
    objetivo = models.TextField(null=True, blank=True)
    mensaje = models.TextField(null=True, blank=True)
    estado = models.ForeignKey(Estado, on_delete=models.SET_NULL, null=True, default=None)
    image = models.ImageField(upload_to='app/static/images/')

    def save(self, *args, **kwargs):
        if not self.estado:
            estado_pendiente = Estado.objects.filter(nombre='Pendiente').first()
            if estado_pendiente:
                self.estado = estado_pendiente
        super().save(*args, **kwargs)