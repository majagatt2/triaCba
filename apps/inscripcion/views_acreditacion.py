"""
Pantalla de acreditacion para la mesa del evento (sin entrar al Admin).

- /inscripcion/acreditacion/            eventos de estos dias para elegir
- /inscripcion/acreditacion/<evento>/   buscar atleta (DNI, apellido, nombre o Nº corredor),
                                         ver su ficha y acreditarlo

Pueden entrar el staff y los usuarios del grupo "Acreditador" (se crea en el Admin, en
Grupos, y se le agrega a cada voluntario de la mesa). Usa el mismo campo "Acreditado" del
Admin, asi que se puede acreditar desde los dos lados.

Pensado para sumar mas adelante: lectura de QR (el campo de busqueda ya recibe lo que
"escribe" un lector USB) y asignacion automatica de numeros por rango de modalidad
(hoy el Nº de corredor se carga a mano y se controla que no este repetido en el evento).
"""
from datetime import timedelta
from zoneinfo import ZoneInfo

from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from urllib.parse import urlencode

from apps.inscripcion.models import Eventos, Inscripcion, hoy_cordoba

GRUPO_ACREDITADOR = 'Acreditador'
ZONA = ZoneInfo('America/Argentina/Cordoba')
DIAS_ANTES = 3      # eventos que se muestran: desde hace 3 dias...
DIAS_DESPUES = 30   # ...hasta dentro de 30 dias
MAX_RESULTADOS = 30


def puede_acreditar(user):
    return user.is_authenticated and (
        user.is_staff or user.groups.filter(name=GRUPO_ACREDITADOR).exists())


solo_acreditadores = user_passes_test(puede_acreditar)


def _archivo_cargado(archivo, default):
    """True si el FileField tiene un archivo real (no el valor por defecto del modelo)."""
    nombre = getattr(archivo, 'name', '') or ''
    return bool(nombre) and nombre != default


def ficha(inscripcion):
    """Lo que la mesa necesita controlar de una inscripcion."""
    p = inscripcion.persona
    edad = inscripcion.get_edad
    alertas = []
    pago_ok = inscripcion.confirm_pago
    if not pago_ok:
        alertas.append('Inscripción NO aprobada (falta revisar pago, certificado y datos).')
    certificado_ok = _archivo_cargado(inscripcion.emmac_file, 'emmac_file')
    if not certificado_ok:
        alertas.append('Falta certificado médico / EMMAC.')
    menor = edad < 18
    if menor and not (inscripcion.responsable_tutor and inscripcion.telefono_responsable):
        alertas.append('Es menor y faltan datos del responsable.')
    acreditado_en = (timezone.localtime(inscripcion.acreditado_en, ZONA)
                     if inscripcion.acreditado_en else None)
    return {
        'i': inscripcion,
        'p': p,
        'edad': edad,
        'menor': menor,
        'pago_ok': pago_ok,
        'certificado_ok': certificado_ok,
        'certificado_url': inscripcion.emmac_file.url if certificado_ok else '',
        'dni_url': p.fotoDni.url if _archivo_cargado(p.fotoDni, 'foto Dni') else '',
        'comprobante_url': (inscripcion.comprobPago.url
                            if _archivo_cargado(inscripcion.comprobPago, 'media/pagos/sin_costo.jpg') else ''),
        'alertas': alertas,
        'acreditado_en': acreditado_en,
    }


@login_required
@solo_acreditadores
def acreditacion_inicio(request):
    hoy = hoy_cordoba()
    eventos = (Eventos.objects
               .filter(fechaEvento__gte=hoy - timedelta(days=DIAS_ANTES),
                       fechaEvento__lte=hoy + timedelta(days=DIAS_DESPUES))
               .select_related('tipo')
               .annotate(n_inscriptos=Count('inscripcion'),
                         n_aprobados=Count('inscripcion', filter=Q(inscripcion__confirm_pago=True)),
                         n_acreditados=Count('inscripcion', filter=Q(inscripcion__acreditacion=True)))
               .order_by('fechaEvento'))
    return render(request, 'inscripcion/acreditacion/inicio.html', {'eventos': eventos, 'hoy': hoy})


def _buscar(evento, q):
    base = (Inscripcion.objects.filter(eventoRelacionado=evento)
            .select_related('persona'))
    q = (q or '').strip()
    if not q:
        return base.none()
    if q.isdigit():
        # DNI exacto o Nº de corredor exacto primero (lo normal en la mesa); si no hay, DNI parcial
        exactos = base.filter(Q(persona__dni=q) | Q(numero=int(q)))
        if exactos.exists():
            return exactos.order_by('persona__last_name')
        return base.filter(persona__dni__icontains=q).order_by('persona__last_name')
    filtro = Q()
    for palabra in q.split():
        filtro &= Q(persona__last_name__icontains=palabra) | Q(persona__first_name__icontains=palabra)
    return base.filter(filtro).order_by('persona__last_name', 'persona__first_name')


def _resumen(evento):
    filas = (Inscripcion.objects.filter(eventoRelacionado=evento)
             .values('modalidad')
             .annotate(total=Count('id'),
                       aprobados=Count('id', filter=Q(confirm_pago=True)),
                       acreditados=Count('id', filter=Q(acreditacion=True)))
             .order_by('modalidad'))
    filas = list(filas)
    total = {
        'total': sum(f['total'] for f in filas),
        'aprobados': sum(f['aprobados'] for f in filas),
        'acreditados': sum(f['acreditados'] for f in filas),
    }
    return filas, total


def _numero_repetido(inscripcion, numero):
    if not numero:
        return None
    return (Inscripcion.objects
            .filter(eventoRelacionado=inscripcion.eventoRelacionado, numero=numero)
            .exclude(pk=inscripcion.pk).select_related('persona').first())


def _avisar(request, tipo, texto):
    """Aviso que se muestra arriba de la pantalla (no se usa el sistema de mensajes de Django
    porque la plantilla base lo muestra como ventana emergente, y en la mesa molesta)."""
    request.session['acreditacion_aviso'] = {'tipo': tipo, 'texto': texto}


LISTAS = {
    'pendientes': ('Para acreditar', Q(confirm_pago=True, acreditacion=False)),
    'acreditados': ('Acreditados', Q(acreditacion=True)),
    'sinaprobar': ('Sin aprobar', Q(confirm_pago=False, acreditacion=False)),
    'todos': ('Todos', Q()),
}


def _listado(evento, ver, modalidad):
    """Listado completo del evento para el control visual en la mesa (ordenado por apellido)."""
    base = Inscripcion.objects.filter(eventoRelacionado=evento)
    if modalidad:
        base = base.filter(modalidad=modalidad)
    filtros = [{'clave': k, 'nombre': n, 'cantidad': base.filter(f).count()} for k, (n, f) in LISTAS.items()]
    filas = (base.filter(LISTAS[ver][1]).select_related('persona')
             .order_by('persona__last_name', 'persona__first_name'))
    return filtros, filas


def _url_volver(url_evento, datos, insc_pk=None):
    """Despues de acreditar, volver al listado (con el mismo filtro y en la misma fila) si se vino de ahi."""
    ver = datos.get('ver')
    if ver not in LISTAS:
        return url_evento
    params = {'ver': ver}
    if datos.get('mod'):
        params['mod'] = datos['mod']
    return f'{url_evento}?{urlencode(params)}' + (f'#i{insc_pk}' if insc_pk else '')


def _entero(valor):
    valor = (valor or '').strip()
    return int(valor) if valor.isdigit() else None


@login_required
@solo_acreditadores
def acreditacion_evento(request, pk):
    evento = get_object_or_404(Eventos.objects.select_related('tipo'), pk=pk)
    url_evento = reverse('acreditacion_evento', args=[evento.pk])

    if request.method == 'POST':
        insc = get_object_or_404(Inscripcion.objects.select_related('persona'),
                                 pk=request.POST.get('inscripcion'), eventoRelacionado=evento)
        nombre = f'{insc.persona.last_name}, {insc.persona.first_name}'
        accion = request.POST.get('accion')
        volver = f'{url_evento}?id={insc.pk}'
        if request.POST.get('ver') in LISTAS:
            volver += '&' + urlencode({k: request.POST[k] for k in ('ver', 'mod') if request.POST.get(k)})
        if accion == 'acreditar':
            numero = _entero(request.POST.get('numero'))
            chip = _entero(request.POST.get('chip'))
            otro = _numero_repetido(insc, numero)
            if otro:
                _avisar(request, 'error', f'El Nº {numero} ya lo tiene {otro.persona.last_name}, '
                                        f'{otro.persona.first_name}. No se acreditó.')
                return redirect(volver)
            insc.numero = numero or 0
            insc.numero_chip = chip or 0
            insc.acreditacion = True
            insc.acreditado_en = timezone.now()
            insc.acreditado_por = request.user
            insc.save(update_fields=['numero', 'numero_chip', 'acreditacion',
                                     'acreditado_en', 'acreditado_por'])
            _avisar(request, 'ok', f'✔ {nombre} acreditado/a' + (f' con el Nº {numero}.' if numero else '.'))
            return redirect(_url_volver(url_evento, request.POST, insc.pk))
        if accion == 'aprobar':
            # solo administradores: aprobar la inscripcion ahi mismo (pago + certificado + revision general) (mismo efecto que tildar CP y Aprobado en el Admin)
            if not request.user.is_staff:
                _avisar(request, 'error', 'Solo un administrador puede aprobar inscripciones.')
                return redirect(volver)
            insc.control_pago = True
            insc.confirm_pago = True
            insc.save(update_fields=['control_pago', 'confirm_pago'])
            _avisar(request, 'ok', f'Inscripción de {nombre} aprobada. Ya se puede acreditar.')
            return redirect(volver)
        if accion == 'deshacer':
            insc.acreditacion = False
            insc.acreditado_en = None
            insc.acreditado_por = None
            insc.save(update_fields=['acreditacion', 'acreditado_en', 'acreditado_por'])
            _avisar(request, 'aviso', f'Se quitó la acreditación de {nombre}.')
            return redirect(volver)
        return redirect(url_evento)

    q = request.GET.get('q', '')
    ver = request.GET.get('ver', '')
    ver = ver if ver in LISTAS else ''
    mod = request.GET.get('mod', '')
    elegida = None
    resultados = []
    if request.GET.get('id'):
        elegida = (Inscripcion.objects.filter(eventoRelacionado=evento, pk=request.GET['id'])
                   .select_related('persona', 'acreditado_por').first())
    elif q:
        resultados = list(_buscar(evento, q)[:MAX_RESULTADOS + 1])
        if len(resultados) == 1:
            elegida = resultados[0]
            resultados = []

    filas, total = _resumen(evento)
    filtros, listado = (_listado(evento, ver, mod) if ver and not elegida else ([], []))
    contexto = {
        'ver': ver,
        'mod': mod,
        'filtros': filtros,
        'listado': listado,
        'modalidades': [f['modalidad'] for f in filas],
        'url_lista': _url_volver(url_evento, {'ver': ver, 'mod': mod}) if ver else '',
        'aviso': request.session.pop('acreditacion_aviso', None),
        'evento': evento,
        'q': q,
        'resultados': resultados[:MAX_RESULTADOS],
        'hay_mas': len(resultados) > MAX_RESULTADOS,
        'ficha': ficha(elegida) if elegida else None,
        'resumen': filas,
        'total': total,
    }
    return render(request, 'inscripcion/acreditacion/evento.html', contexto)
