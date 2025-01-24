from django.db import models
from django.contrib.auth.models import User

class MantenimientoPreventivo(models.Model):
    tarea_mantenimiento = models.OneToOneField('TareaMantenimiento', on_delete=models.CASCADE, related_name='informe_mantenimiento', blank=True, null=True)
    tipo_ot = models.CharField(max_length=30, blank=False, null=True)
    asignado_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asignado_mantenimiento', blank=True, null=True)
    solicitante = models.CharField(max_length=300, blank=False, null=True)
    prioridad = models.CharField(max_length=50, choices=[('Alta', 'Alta'), ('Media', 'Media'), ('Baja', 'Baja')])
    programado_para = models.DateField(max_length=50, blank=False, null=True)
    turno = models.CharField(max_length=50, choices=[('Dia', 'Dia'), ('Noche', 'Noche')])
    descripcion_trabajo = models.TextField( blank=False, null=True)
    cod_equipo = models.CharField(max_length=50, blank=False, null=True)
    equipo = models.CharField(max_length=50, blank=False, null=True)
    observaciones = models.TextField(blank=True, null=True, default='No se han registrado observaciones')
    realizado_por = models.CharField(max_length=30, blank=True, null=True)
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='supervisado_por', blank=True)
    fecha = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    tabla_dinamica = models.JSONField(default=list)


class TareaMantenimiento(models.Model):
    estado = models.CharField(max_length=50, choices=[('En Curso', 'En Curso'), ('Revision', 'Revision'), ('Archivada', 'Archivada')], default= 'En Curso')
    asignado_a = models.ForeignKey(User, on_delete=models.CASCADE, related_name='asignado_tarea')
    creada = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    creado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creador')
    supervisor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='supervisor_tarea', blank=True)
    tipo_ot = models.CharField(max_length=30, blank=False, null=True)
    descripcion_trabajo = models.TextField(blank=False, null=True)