"""
{% version_estaticos %} devuelve un numero que cambia cada vez que se reinicia el sitio
(cada deploy hace touch al wsgi). Se agrega a los links de CSS/JS propios
(tema.css?v=...) para que los navegadores, sobre todo en el celular, bajen la version
nueva en vez de usar la que tienen guardada.
"""
import time

from django import template
from django.conf import settings

register = template.Library()

_VERSION = str(int(time.time()))


@register.simple_tag
def version_estaticos():
    return _VERSION


@register.simple_tag
def sitio_url():
    """Direccion publica del sitio, sin / al final (settings.SITIO_URL). Para los links de los mails:
    <a href="{% sitio_url %}/accounts/login/">"""
    return settings.SITIO_URL


@register.filter
def clave(diccionario, k):
    """{{ dic|clave:x }} -> dic[x] (o vacio si no esta). Para tablas armadas en la vista."""
    try:
        return diccionario.get(k, '')
    except AttributeError:
        return ''


@register.filter
def contiene(conjunto, k):
    """{% if conjunto|contiene:x %}"""
    try:
        return k in conjunto
    except TypeError:
        return False
