from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth.password_validation import validate_password

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
