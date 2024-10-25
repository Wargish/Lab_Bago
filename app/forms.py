from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import *


class RegistroForm(forms.ModelForm):
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
    class Meta:
        model = User
        fields = ['username', 'password']

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


class InformeForm(forms.ModelForm):
    class Meta:
        model = InformeCondiciones
        fields = ['user', 'lugar', 'tipo_Informe', 'objetivo', 'mensaje', 'image']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'lugar': forms.Select(attrs={'class': 'form-control'}),
            'tipo_Informe': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class TareaForm(forms.ModelForm):
    class Meta:
        model = Tarea
        fields = ['informe', 'objetivo', 'estado', 'tecnico']
        widgets = {
            'informe': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'tecnico': forms.Select(attrs={'class': 'form-control'}),
        }

class ReporteForm(forms.ModelForm):
    class Meta:
        model = Reporte
        fields = ['contenido', 'imagen']
        widgets = {
            'contenido': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }