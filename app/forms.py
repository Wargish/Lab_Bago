from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from .models import *


class RegistroForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

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


class InformeForm(forms.ModelForm):
    class Meta:
        model = Informe
        fields = ['user', 'lugar', 'objetivo', 'mensaje', 'image']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control'}),
            'lugar': forms.Select(attrs={'class': 'form-control'}),
            'objetivo': forms.TextInput(attrs={'class': 'form-control'}),
            'mensaje': forms.Textarea(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
