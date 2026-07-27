import re
from django.core.exceptions import ValidationError


class PasswordComplexityValidator:

    def validate(self, password, user=None):
        if not re.search(r'[A-Z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra mayúscula.")

        if not re.search(r'[a-z]', password):
            raise ValidationError("La contraseña debe contener al menos una letra minúscula.")

        if not re.search(r'\d', password):
            raise ValidationError("La contraseña debe contener al menos un número.")

        if not re.search(r'[!@#$%^&*(),.?":{}|<>_\-+=/]', password):
            raise ValidationError("La contraseña debe contener al menos un carácter especial.")

    def get_help_text(self):
        return (
            "Debe contener mayúsculas, minúsculas, "
            "números y caracteres especiales."
        )