"""
{% version_estaticos %} devuelve un numero que cambia cada vez que se reinicia el sitio
(cada deploy hace touch al wsgi). Se agrega a los links de CSS/JS propios
(tema.css?v=...) para que los navegadores, sobre todo en el celular, bajen la version
nueva en vez de usar la que tienen guardada.
"""
import time

from django import template

register = template.Library()

_VERSION = str(int(time.time()))


@register.simple_tag
def version_estaticos():
    return _VERSION
