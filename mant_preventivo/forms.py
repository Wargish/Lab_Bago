from django import forms
from .models import *

# Formulario para supervisores
class TareaMantenimientoForm(forms.ModelForm):
    class Meta:
        model = TareaMantenimiento
        fields = ['asignado_a']

    def __init__(self, *args, **kwargs):
        super(TareaMantenimientoForm, self).__init__(*args, **kwargs)
        tecnicos_externos = User.objects.filter(groups__name__in=['Técnico', 'Externo'])
        self.fields['asignado_a'].queryset = tecnicos_externos



class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = MantenimientoPreventivo
        fields = ['tipo_ot', 'asignado_a', 'solicitante', 'prioridad', 'tarea_mantenimiento', 'programado_para', 'supervisor', 'turno']

    def __init__(self, *args, **kwargs):
        super(MantenimientoForm, self).__init__(*args, **kwargs)
        tecnicos_externos = User.objects.filter(groups__name__in=['Técnico', 'Externo'])
        self.fields['asignado_a'].queryset = tecnicos_externos

# Formulario para la tabla dinámica
class TablaDinamicaForm(forms.ModelForm):
    class Meta:
        model = TablaDinamica
        fields = ['columna1', 'columna2', 'columna3','columna4']