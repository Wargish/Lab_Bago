from django.db import models
from django.contrib.auth.models import User

class MantenimientoPreventivo(models.Model):
    tarea_mantenimiento = models.OneToOneField('TareaMantenimiento', on_delete=models.CASCADE, related_name='informe_mantenimiento', blank=True, null=True)
    tipo_ot = models.CharField(max_length=30)
    asignado_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asignado_mantenimiento')
    solicitante = models.CharField(max_length=300)
    prioridad = models.CharField(max_length=50, choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')])
    programado_para = models.CharField(max_length=50)
    turno = models.CharField(max_length=50, choices=[('Dia', 'Dia'), ('Noche', 'Noche')])
    descripcion_trabajo = models.TextField(max_length=100)
    cod_equipo = models.CharField(max_length=50)
    equipo = models.CharField(max_length=50)
    observaciones = models.TextField(blank=True, null=True)
    realizado_por = models.CharField(max_length=30, blank=True, null=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='supervisado_por')
    fecha = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)


class TareaMantenimiento(models.Model):
    estado = models.CharField(max_length=50, choices=[('En Curso', 'En Curso'), ('Revision', 'Revision'), ('Archivada', 'Archivada')])
    asignado_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asignado_tarea')
    creada = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creador')


class TablaDinamica(models.Model):
    informe = models.ForeignKey(MantenimientoPreventivo, on_delete=models.CASCADE, related_name='tabla_dinamica')
    columna1 = models.CharField(max_length=100)
    columna2 = models.CharField(max_length=100, blank=True, null=True)
    columna3 = models.CharField(max_length=100, blank=True, null=True)
