from django import forms
from .models import *

# Formulario para supervisores
class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = MantenimientoPreventivo
        fields = ['tipo_ot', 'asignado_a', 'solicitante', 'prioridad', 'tarea_mantenimiento', 'programado_para', 'supervisor', 'turno']

# Formulario para la tabla dinámica
class TablaDinamicaForm(forms.ModelForm):
    class Meta:
        model = TablaDinamica
        fields = ['columna1', 'columna2', 'columna3']