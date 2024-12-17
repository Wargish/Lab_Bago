import re
from django.core.exceptions import ValidationError

class SpecialCharacterValidator:
    def validate(self, password, user=None):
        if not re.findall('[^A-Za-z0-9]', password):
            raise ValidationError('La Contraseña debe tener al menos un caracter especial')

    def get_help_text(self):
        return 'Tu Contraseña debe tener al menos un caracter especial.'



class UppercaseValidator:
    def validate(self, password, user=None):
        if not any(char.isupper() for char in password):
            raise ValidationError('La Contraseña debe tener al menos una letra Mayúscula.')

    def get_help_text(self):
        return 'Tu Contraseña debe tener al menos una letra Mayúscula.'