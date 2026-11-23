"""
Miniaturas livianas para las listas del Admin.

Antes las listas mostraban la foto ORIGINAL (comprobante, certificado, DNI) achicada a 40x40 con
HTML: el navegador igual bajaba la foto completa (1-4 MB cada una) y una pagina de 20 inscripciones
con 3 fotos podia pesar 100 MB o mas. Ahora se genera una sola vez una miniatura de ~5 KB en
media/miniaturas/ y se muestra esa; al tocarla se abre el archivo original en otra pestaña.
"""
import hashlib
import logging
import os

from django.conf import settings
from django.utils.html import format_html

log = logging.getLogger(__name__)

EXTENSIONES_IMAGEN = ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp')
CARPETA = 'miniaturas'


def _ruta_miniatura(nombre, mtime, lado):
    clave = hashlib.md5(f'{nombre}|{mtime}|{lado}'.encode()).hexdigest()
    return f'{CARPETA}/{clave[:2]}/{clave}.jpg'


def miniatura_url(archivo, lado=120):
    """URL de una miniatura del archivo (la crea si no existe). None si no es una imagen o falla."""
    nombre = getattr(archivo, 'name', '') or ''
    if not nombre.lower().endswith(EXTENSIONES_IMAGEN):
        return None
    try:
        origen = archivo.path
        if not os.path.exists(origen):
            return None
        relativa = _ruta_miniatura(nombre, int(os.path.getmtime(origen)), lado)
        destino = os.path.join(settings.MEDIA_ROOT, relativa)
        if not os.path.exists(destino):
            from PIL import Image, ImageOps
            os.makedirs(os.path.dirname(destino), exist_ok=True)
            with Image.open(origen) as img:
                img = ImageOps.exif_transpose(img)
                img.thumbnail((lado, lado))
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')
                img.save(destino, 'JPEG', quality=70, optimize=True)
        return settings.MEDIA_URL + relativa
    except Exception:   # archivo roto, permisos, etc.: se muestra solo el link
        log.warning('No se pudo crear la miniatura de %s', nombre, exc_info=True)
        return None


def miniatura_html(archivo, lado_mostrado=40):
    """Miniatura clickeable (abre el original en otra pestaña). Si no es imagen: link 'PDF' o 'Ver'."""
    nombre = getattr(archivo, 'name', '') or ''
    if not nombre:
        return '—'
    try:
        url = archivo.url
    except Exception:
        return '—'
    mini = miniatura_url(archivo)
    if mini:
        return format_html(
            '<a href="{}" target="_blank" rel="noopener"><img src="{}" width="{}" height="{}" '
            'loading="lazy" style="object-fit:cover;border-radius:4px" alt="ver"></a>',
            url, mini, lado_mostrado, lado_mostrado)
    texto = 'PDF' if nombre.lower().endswith('.pdf') else 'Ver'
    return format_html('<a href="{}" target="_blank" rel="noopener"><b>{}</b></a>', url, texto)
