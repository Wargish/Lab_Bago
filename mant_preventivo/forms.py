from django import forms
from django.core.exceptions import ValidationError

from .models import *

# Formulario para supervisores
class TareaMantenimientoForm(forms.ModelForm):
    class Meta:
        model = TareaMantenimiento
        fields = ['asignado_a', 'tipo_ot', 'descripcion_trabajo']  # Agregar los nuevos campos

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['asignado_a'].queryset = User.objects.filter(groups__name__in=['Técnico', 'Externo'])


class MantenimientoForm(forms.ModelForm):
    programado_para = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        required=True
    )
    class Meta:
        model = MantenimientoPreventivo
        fields = ['solicitante', 'prioridad', 'programado_para', 'turno', 'cod_equipo', 'equipo', 'observaciones']
        widgets = {
            'programado_para': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }