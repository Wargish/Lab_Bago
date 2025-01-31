from django import forms
from internal_workers.models import Zona, UbicacionTecnica, Equipo, Informe, Tarea, ReporteTarea, FeedbackTarea 

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['categoría', 'zona', 'ubicacion_tecnica', 'equipo', 'objetivo', 'mensaje', 'imagen']
        widgets = {
            'categoría': forms.Select(attrs={'class': 'form-control'}),
            'zona': forms.Select(attrs={'class': 'form-control'}),
            'ubicacion_tecnica': forms.Select(attrs={'class': 'form-control'}),
            'equipo': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['informe', 'objetivo', 'estado', 'asignado_a']
        widgets = {
            'informe': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'asignado_a': forms.Select(attrs={'class': 'form-control'}),
        }

class ReporteForm(forms.ModelForm):
    class Meta:
        model = ReporteTarea
        fields = ['tarea', 'contenido', 'imagen']
        widgets = {
            'tarea': forms.HiddenInput(),
            'contenido': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = FeedbackTarea
        fields = ['tarea', 'aprobado', 'comentarios']
        widgets = {
            'tarea': forms.HiddenInput(),
            'aprobado': forms.RadioSelect(choices=[(True, 'Sí'), (False, 'No')]),
            'comentarios': forms.Textarea(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        conforme = cleaned_data.get('aprobado')
        comentario = cleaned_data.get('comentarios')

        if conforme is False and not comentario:
            self.add_error('comentarios', 'Este campo es obligatorio si no está conforme.')

        return cleaned_data
    
