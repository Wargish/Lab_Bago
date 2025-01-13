from django import forms
from django.core.exceptions import ValidationError

from .models import *

# Formulario para supervisores
class TareaMantenimientoForm(forms.ModelForm):
    class Meta:
        model = TareaMantenimiento
        fields = ['asignado_a']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asignado_a'].queryset = User.objects.filter(groups__name__in=['Técnico', 'Externo'])


class MantenimientoForm(forms.ModelForm):
    class Meta:
        model = MantenimientoPreventivo
        fields = ['tipo_ot', 'asignado_a', 'solicitante', 'prioridad', 'tarea_mantenimiento', 'programado_para', 'turno','descripcion_trabajo','cod_equipo','equipo','observaciones','realizado_por','supervisor']
        widgets = {
            'programado_para': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'descripcion_trabajo': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }
        
    def __init__(self, *args, **kwargs):
        super(MantenimientoForm, self).__init__(*args, **kwargs)
        tecnicos_externos = User.objects.filter(groups__name__in=['Técnico', 'Externo'])
        self.fields['asignado_a'].queryset = tecnicos_externos