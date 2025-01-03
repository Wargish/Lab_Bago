from django import forms
from .models import *

# Formulario para supervisores
class MantenimientoSupervisorForm(forms.ModelForm):
    class Meta:
        model = MantenimientoPreventivo
        fields = ['tipo_ot', 'asignado_a', 'solicitante', 'prioridad', 'tarea', 'programado_para', 'supervisor', 'turno']

# Formulario para técnicos/externos
class MantenimientoAsignadoForm(forms.ModelForm):
    class Meta:
        model = MantenimientoPreventivo
        fields = ['observaciones']

# Formulario para la tabla dinámica
class TablaDinamicaForm(forms.ModelForm):
    class Meta:
        model = TablaDinamica
        fields = ['columna1', 'columna2', 'columna3']

