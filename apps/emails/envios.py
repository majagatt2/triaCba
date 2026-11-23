"""
Envio de emails masivos por tandas.

Por que: Gmail permite unos 500 destinatarios por dia desde una cuenta comun. Antes el modulo mandaba
todo de una vez (bloques de 50 en CCO, dentro del mismo pedido web): un envio a "Todas las personas"
agotaba el cupo del dia y Google bloqueaba tambien los mails de confirmacion de inscripcion.

Como funciona ahora:
  1. Al publicar un email se arma la lista de destinatarios (EnvioEmail, uno por direccion, sin repetir).
  2. enviar_tanda() manda hasta EMAILS_POR_TANDA mails, sin pasar EMAILS_LIMITE_DIARIO en 24 horas,
     de a uno por destinatario (nadie ve los demas correos) y con una pausa corta entre cada uno.
  3. Una tarea programada de PythonAnywhere corre cada hora `python manage.py enviar_newsletters`.
     Tambien se puede apretar "Enviar una tanda ahora" en el modulo de emails.
El cupo deja margen para los mails de inscripcion, que salen por la misma cuenta.
"""
import logging
import re
import time
from datetime import timedelta

from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.core.validators import validate_email
from django.db.models import Count
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags

from apps.emails.models import EnvioEmail

log = logging.getLogger(__name__)

LIMITE_DIARIO = getattr(settings, 'EMAILS_LIMITE_DIARIO', 300)
POR_TANDA = getattr(settings, 'EMAILS_POR_TANDA', 40)
PAUSA = getattr(settings, 'EMAILS_PAUSA_SEGUNDOS', 1.5)
EMAIL_ASOCIACION = 'triatloncba@gmail.com'


# ---------------------------------------------------------------- destinatarios

GRUPOS = [
    ('Nadie', 'Nadie (solo el destinatario de "Para")'),
    ('Asociados', 'Socios activos'),
    ('Asociados_Escuela', 'Escuela (socios activos que asisten)'),
    ('Asociados_con_acceso_Kempes', 'Socios con acceso Kempes'),
    ('Todas_las_Personas', 'Todas las personas registradas'),
]


def _limpiar(emails):
    """Sin repetidos (sin importar mayusculas) y solo direcciones validas, en el orden original."""
    vistos, salida = set(), []
    for e in emails:
        e = (e or '').strip()
        clave = e.lower()
        if not e or clave in vistos:
            continue
        try:
            validate_email(e)
        except ValidationError:
            continue
        vistos.add(clave)
        salida.append(e)
    return salida


def _socios_al_dia(**filtro):
    from apps.socio.models import Asociado
    socios = Asociado.objects.filter(**filtro).select_related('persona', 'tipoAsociado')
    return [a.persona.email for a in socios if a.persona and a.get_estado]


def emails_del_grupo(grupo):
    """Direcciones de un grupo (clave de GRUPOS o id de un evento)."""
    from apps.inscripcion.models import Inscripcion
    from apps.usuarios.models import Persona
    grupo = str(grupo or '')
    if grupo.isdigit():
        return _limpiar(Inscripcion.objects.filter(eventoRelacionado_id=int(grupo))
                        .values_list('persona__email', flat=True))
    if grupo == 'Asociados':
        return _limpiar(_socios_al_dia())
    if grupo == 'Asociados_con_acceso_Kempes':
        return _limpiar(_socios_al_dia(tipoAsociado=1))
    if grupo == 'Asociados_Escuela':
        return _limpiar(_socios_al_dia(tipoAsociado=5, asiste=True))
    if grupo == 'Todas_las_Personas':
        return _limpiar([EMAIL_ASOCIACION] + list(Persona.objects.exclude(email='').values_list('email', flat=True)))
    return []


def nombre_del_grupo(grupo):
    from apps.inscripcion.models import Eventos
    grupo = str(grupo or '')
    if grupo.isdigit():
        evento = Eventos.objects.filter(pk=int(grupo)).first()
        return f'Inscriptos: {evento}' if evento else 'Inscriptos de un evento'
    return dict(GRUPOS).get(grupo, grupo)


def encolar(newsletter):
    """Crea un EnvioEmail pendiente por destinatario (el 'Para' + el grupo). Devuelve cuantos nuevos."""
    destinatarios = _limpiar([newsletter.email] + emails_del_grupo(newsletter.bcc))
    existentes = set(e.lower() for e in newsletter.envios.values_list('email', flat=True))
    nuevos = [EnvioEmail(newsletter=newsletter, email=e) for e in destinatarios if e.lower() not in existentes]
    EnvioEmail.objects.bulk_create(nuevos, ignore_conflicts=True)
    return len(nuevos)


# ---------------------------------------------------------------- armado del mensaje

def _urls_absolutas(html):
    """Las imagenes que se suben con el editor quedan como /media/...; en un email tienen que ser
    direcciones completas (https://portal.triatloncordoba.org/media/...) o no se ven."""
    base = settings.SITIO_URL.rstrip('/')
    return re.sub(r'''(src|href)=(["'])/(?!/)''', lambda m: f'{m.group(1)}={m.group(2)}{base}/', html or '')


def armar_mensaje(newsletter, para, conexion=None):
    cuerpo = _urls_absolutas(newsletter.body)
    html = render_to_string('emails/email_masivo.html', {
        'cuerpo': cuerpo, 'asunto': newsletter.subject, 'sitio_url': settings.SITIO_URL.rstrip('/'),
    })
    texto = re.sub(r'\n{3,}', '\n\n', strip_tags(cuerpo.replace('<br', '\n<br').replace('</p>', '</p>\n'))).strip()
    msg = EmailMultiAlternatives(newsletter.subject, texto or newsletter.subject, settings.EMAIL_HOST_USER,
                                 [para], connection=conexion, reply_to=[EMAIL_ASOCIACION])
    msg.attach_alternative(html, 'text/html')
    for adjunto in newsletter.adjuntos.all():
        try:
            with adjunto.archivo.open('rb') as f:
                msg.attach(str(adjunto), f.read())
        except OSError:
            log.warning('No se encontro el adjunto %s del email %s', adjunto.archivo.name, newsletter.pk)
    return msg


def enviar_prueba(newsletter, para):
    """Manda el email a una sola direccion (para revisar como se ve). No cuenta como envio masivo."""
    armar_mensaje(newsletter, para).send(fail_silently=False)


# ---------------------------------------------------------------- envio por tandas

def cupo_disponible():
    hace_24h = timezone.now() - timedelta(hours=24)
    usados = EnvioEmail.objects.filter(estado=EnvioEmail.ENVIADO, enviado_en__gte=hace_24h).count()
    return max(0, LIMITE_DIARIO - usados)


def _es_limite_de_gmail(error):
    texto = str(error)
    return '5.4.5' in texto or 'sending limit' in texto.lower() or '4.7.0' in texto


def enviar_tanda(limite=None, pausa=None):
    """Envia la proxima tanda de pendientes (de todos los emails, en orden). Devuelve un resumen."""
    pausa = PAUSA if pausa is None else pausa
    cantidad = min(cupo_disponible(), POR_TANDA if limite is None else limite)
    resumen = {'enviados': 0, 'errores': 0, 'cupo': cantidad, 'frenado_por_gmail': False,
               'pendientes': EnvioEmail.objects.filter(estado=EnvioEmail.PENDIENTE).count()}
    if cantidad <= 0 or not resumen['pendientes']:
        return resumen

    tanda = list(EnvioEmail.objects.filter(estado=EnvioEmail.PENDIENTE)
                 .select_related('newsletter').order_by('id')[:cantidad])
    conexion = get_connection(fail_silently=False)
    try:
        conexion.open()
        for n, envio in enumerate(tanda):
            try:
                armar_mensaje(envio.newsletter, envio.email, conexion).send()
            except Exception as e:  # SMTP: un destinatario malo no frena la tanda; el limite de Gmail si
                if _es_limite_de_gmail(e):
                    resumen['frenado_por_gmail'] = True
                    log.warning('Gmail limito los envios: se frena la tanda (%s)', e)
                    break
                envio.estado, envio.error = EnvioEmail.ERROR, str(e)[:500]
                envio.save(update_fields=['estado', 'error'])
                resumen['errores'] += 1
                continue
            envio.estado, envio.enviado_en, envio.error = EnvioEmail.ENVIADO, timezone.now(), ''
            envio.save(update_fields=['estado', 'enviado_en', 'error'])
            resumen['enviados'] += 1
            if pausa and n < len(tanda) - 1:
                time.sleep(pausa)
    finally:
        try:
            conexion.close()
        except Exception:
            pass
    resumen['pendientes'] = EnvioEmail.objects.filter(estado=EnvioEmail.PENDIENTE).count()
    return resumen


def progreso(newsletter):
    filas = dict(newsletter.envios.order_by().values_list('estado').annotate(n=Count('id')))
    total = sum(filas.values())
    return {'total': total, 'enviados': filas.get(EnvioEmail.ENVIADO, 0),
            'pendientes': filas.get(EnvioEmail.PENDIENTE, 0), 'errores': filas.get(EnvioEmail.ERROR, 0)}
