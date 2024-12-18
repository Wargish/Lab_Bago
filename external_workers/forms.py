from django import forms
from .models import *



class SolicitudExternoForm(forms.ModelForm):
    externo = forms.ModelChoiceField(
        queryset=User.objects.filter(groups__name='Externo'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Usuario Externo',
        error_messages={
            'required': 'Este campo es obligatorio.',
            }
        )


    class Meta:
        model = SolicitudExterno
        fields = ['externo','objetivo','descripcion', 'imagen']
        widgets = {
            'objetivo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Objetivo'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Descripción'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        error_messages={
            'required': 'Este campo es obligatorio.',
            }


class PresupuestoExternoForm(forms.ModelForm):
    class Meta:
        model = PresupuestoExterno
        fields = ['archivo', 'estado', 'mensaje', 'fecha_asistencia']
        widgets = {
            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
            'fecha_asistencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'estado': forms.Select(attrs={'id': 'id_estado'}),
        }


class TareaExternoForm(forms.ModelForm):
    class Meta:
        model = TareaExterno
        fields = ['solicitud', 'estado', 'fecha_asistencia']
        widgets = {
            'solicitud': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_asistencia': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }




class ExternoReporteForm(forms.ModelForm):
    class Meta:
        model = ExternoReporte
        fields = ['tarea_externo', 'descripcion', 'imagen']
        widgets = {
            'tarea_externo': forms.HiddenInput(),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class ExternoFeedbackForm(forms.ModelForm):
    class Meta:
        model = ExternoFeedback
        fields = ['tarea_externo', 'aprobado', 'comentario']
        widgets = {
            'tarea_externo': forms.HiddenInput(),
            'aprobado': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'comentario': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        conforme = cleaned_data.get('aprobado')
        comentario = cleaned_data.get('comentario')

        if conforme is False and not comentario:
            self.add_error('comentario', 'Este campo es obligatorio si no está conforme.')

        return cleaned_data
    
