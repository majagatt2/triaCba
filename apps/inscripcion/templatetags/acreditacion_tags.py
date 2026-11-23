"""{{ request.user|puede_acreditar }}: True si el usuario puede usar la pantalla de acreditacion."""
from django import template

from apps.inscripcion.views_acreditacion import puede_acreditar as _puede

register = template.Library()


@register.filter
def puede_acreditar(user):
    return _puede(user)
