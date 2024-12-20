from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import *
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth.password_validation import validate_password


""""
class RegistroForm(forms.ModelForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu correo electrónico'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su Contraseña'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirme su Contraseña'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')

        if password != password2:
            raise forms.ValidationError('Las contraseñas no coinciden.')

        try:
            validate_password(password2)
        except forms.ValidationError as e:
            raise forms.ValidationError(f'Error en la contraseña: {"; ".join(e.messages)}')

        return cleaned_data

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingresa tu usuario',
            'required': 'required'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ingrese su Contraseña',
            'required': 'required'
        }),
        error_messages={
            'required': 'Este campo es obligatorio.',
        }
    )
    
    # Adding ReCAPTCHA to the Login Form
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
"""

    
"""

class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['ubicacion', 'categoría', 'objetivo', 'mensaje', 'imagen']
        widgets = {
            'ubicacion': forms.Select(attrs={'class': 'form-control'}),
            'categoría': forms.Select(attrs={'class': 'form-control'}),
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
    
"""