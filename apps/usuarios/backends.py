"""
Inicio de sesion con usuario, email o CUIL.

Muchos atletas no recuerdan su nombre de usuario (los creados desde el formulario publico
son codigos como 20d27d913), pero si su email o su CUIL.
"""
from django.contrib.auth.backends import ModelBackend

from apps.usuarios.models import Persona


class UsuarioEmailOCuilBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        if username is None:
            username = kwargs.get(Persona.USERNAME_FIELD)
        if not username or password is None:
            return None
        dato = username.strip()

        candidatos = list(Persona.objects.filter(username=dato)[:1])
        if not candidatos:
            digitos = ''.join(c for c in dato if c.isdigit())
            if '@' in dato:
                # un mismo email puede estar en varias cuentas (p. ej. padres que inscriben a sus hijos)
                candidatos = list(Persona.objects.filter(email__iexact=dato)[:10])
            elif len(digitos) == 11 and len(dato) <= 13:
                candidatos = list(Persona.objects.filter(cuil=digitos)[:1])

        for persona in candidatos:
            if persona.check_password(password) and self.user_can_authenticate(persona):
                return persona
        if not candidatos:
            Persona().set_password(password)   # mismo tiempo de respuesta exista o no la cuenta
        return None
