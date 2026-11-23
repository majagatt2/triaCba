"""
Envio de los mails del sistema (confirmaciones de inscripcion, socios, pagos, recuperar contraseña).

- El HTML sale de una plantilla que extiende email/base_email.html (liviana, estilos en linea).
- Se agrega una version en texto plano: los mails "solo HTML" tienen mas chances de ir a spam.
- Si Gmail falla (limite diario, red, etc.) se registra en el log y NO se corta lo que estaba haciendo
  el atleta: la inscripcion o el pago ya quedaron guardados. Antes eso terminaba en un error 500.
"""
import logging
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

log = logging.getLogger(__name__)

EMAIL_ASOCIACION = 'triatloncba@gmail.com'


def texto_plano(html):
    """Version de texto del HTML (sin estilos ni etiquetas, con saltos de linea razonables)."""
    html = re.sub(r'(?is)<(head|style|script)\b.*?</\1>', '', html or '')
    html = re.sub(r'(?i)<br\s*/?>|</(p|tr|h1|h2|h3|div|li)>', '\n', html)
    html = re.sub(r'(?i)</td>', '  ', html)
    texto = strip_tags(html)
    texto = '\n'.join(' '.join(l.split()) for l in texto.splitlines())
    return re.sub(r'\n{3,}', '\n\n', texto).strip()


def enviar_html(asunto, plantilla, contexto, destinatarios, reply_to=None):
    """Arma y envia el mail. Devuelve True si salio; si falla lo deja en el log y devuelve False."""
    destinatarios = [d for d in dict.fromkeys(destinatarios) if d]
    if not destinatarios:
        return False
    try:
        html = render_to_string(plantilla, contexto)
        msg = EmailMultiAlternatives(asunto, texto_plano(html), settings.EMAIL_HOST_USER, destinatarios,
                                     reply_to=reply_to or [EMAIL_ASOCIACION])
        msg.attach_alternative(html, 'text/html')
        msg.send(fail_silently=False)
        return True
    except Exception:
        log.exception('No se pudo enviar el mail "%s" a %s', asunto, destinatarios)
        return False
