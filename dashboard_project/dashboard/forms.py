from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class BasicUserCreationForm(UserCreationForm):
    """Formulario de registro para usuarios básicos.

    Observaciones:
    - Para simplificar la experiencia de registro se omiten los validadores
      de contraseña definidos globalmente (ej. longitud mínima) y sólo se
      exige que las contraseñas coincidan.
    - Esto afecta únicamente a este formulario; los validadores globales
      en `settings.py` no se modifican.
    """
    email = forms.EmailField(required=True, help_text='Requerido')

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Ya existe un usuario con ese correo.")
        return email

    def clean_password2(self):
        """Override: sólo comprobar que `password1` y `password2` coincidan.

        Evitamos ejecutar los validadores de contraseña configurados en
        `AUTH_PASSWORD_VALIDATORS` para permitir contraseñas cortas si el
        usuario así lo desea (según petición del cliente).
        """
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if not password1 or not password2:
            raise forms.ValidationError("Debe ingresar y confirmar la contraseña.")
        if password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2


class SimpleRegistrationForm(forms.Form):
    """Formulario sencillo para registro sin validadores de contraseña.

    Este formulario evita los validadores globales y sólo comprueba:
    - que `username` y `email` no existan ya
    - que `password1` y `password2` coincidan
    """
    username = forms.CharField(max_length=150, required=True)
    email = forms.EmailField(required=True)
    password1 = forms.CharField(widget=forms.PasswordInput, required=True)
    password2 = forms.CharField(widget=forms.PasswordInput, required=True)

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('Ya existe un usuario con ese nombre de usuario.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario con ese correo.')
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password1')
        p2 = cleaned.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned
