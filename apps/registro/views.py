
from apps.registro.models import Bienvenida
from apps.usuarios.forms import RegistroForm
from apps.usuarios.models import  Persona
from apps.inscripcion.models import Eventos, EventoCosto, EventoDistancia, EventoModalidade, EventoCategoria, EventoFormasPago
from apps.inscripcion.models import Inscripcion, hoy_cordoba
from apps.socio.models import Asociado, AsociadoPagos, AsociadoTipo, EntrenadoresKempe
from django.views.generic import ListView
#from django.urls import reverse_lazy
from apps.escuela.models import EscuelaPagos, EscuelaFormasPago,EscuelaAsignacTurno


#from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from collections import Counter, defaultdict
from django.db.models import Count, Q


def _conteo_por_evento(eventos, **filtro_extra):
    """{evento: (total, confirmados, acreditados)} en UNA consulta, solo eventos con inscriptos."""
    filas = (Inscripcion.objects.filter(eventoRelacionado__in=eventos, **filtro_extra)
             .order_by()  # sin esto el orden por fecha de pago parte los grupos
             .values('eventoRelacionado')
             .annotate(total=Count('id'),
                       confirmados=Count('id', filter=Q(confirm_pago=True)),
                       acreditados=Count('id', filter=Q(confirm_pago=True, acreditacion=True))))
    por_id = {f['eventoRelacionado']: f for f in filas}
    return {e: por_id[e.id] for e in eventos if e.id in por_id}


def _tabla_por_sexo(inscripciones, campo, opciones):
    """Arma {opcion: [total, mujeres, hombres]} como lo hacia el codigo original ('-' en vez de 0)."""
    total, fem, mas = Counter(), Counter(), Counter()
    for valor, sexo in inscripciones:
        clave = str(valor[campo])
        total[clave] += 1
        if sexo == 'F':
            fem[clave] += 1
        elif sexo == 'M':
            mas[clave] += 1
    tabla = {}
    for d in opciones:
        k = str(d)
        if total[k] > 0 and (fem[k] or mas[k]):
            tabla[d] = [total[k], fem[k] or '-', mas[k] or '-']
    return tabla




# Create your views here.







def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


class ResumenViews(ListView):
    model = Persona
    template_name = 'base/index4.html'

    def get_context_data(self, **kwargs):
        context = super(ResumenViews,self).get_context_data(**kwargs)
        context['personas'] = Persona.objects.all()
        context['asociados'] = Asociado.objects.filter(estado=True)
        context['escuela'] = Asociado.objects.filter(estado=True, entrenador=1)


        cant_tiposAsociados = 0
        atletas_x_tipoAsociado = {}
        for e in AsociadoTipo.objects.all():
            atletas_x_tipoAsociado.update(
                {e.tipoAsociado: Asociado.objects.filter(estado=True, tipoAsociado=e.id).count()})
            cant_tiposAsociados += 1

        context['cant_x_tipoAsociado'] = atletas_x_tipoAsociado
        context['cantidadTipos'] = cant_tiposAsociados

        entrenadores_con_atletas = 0
        total_atletas_con_entrenador = 0
        atletas_x_entrenador = {}
        for e in EntrenadoresKempe.objects.all():
            atletas_x_entrenador.update(
                {e.nombre: Asociado.objects.filter(estado=True, entrenador=e.id).count()}
                )
            if e.id != 1 and e.id != 12: #1 es Escuela y 12 es Sinn Entrenador
                total_atletas_con_entrenador += Asociado.objects.filter(
                estado=True, entrenador=e.id).count()
                if Asociado.objects.filter(
                    estado=True, entrenador=e.id).count() > 0:
                    entrenadores_con_atletas += 1

        context['atletas_x_entrenador'] = atletas_x_entrenador
        context['entrenadores'] = entrenadores_con_atletas
        context['con_acceso_kempes'] = total_atletas_con_entrenador

        conteo = _conteo_por_evento(list(Eventos.objects.filter(estado=True)))
        context['eventos'] = {e: [c['total'], c['confirmados']] for e, c in conteo.items()}


        return context


class ResumenViewsEscuela(ListView):
    model = Persona
    template_name = 'base/estad_escuela.html'

    def get_context_data(self, **kwargs):
        context = super(ResumenViewsEscuela, self).get_context_data(**kwargs)
        context['escuela'] = Asociado.objects.filter(
            estado=True, entrenador=1)
        context['escuela_no_asisten'] = Asociado.objects.filter(
            estado=True, entrenador=1,asiste=False)
        context['escuela_asisten'] = Asociado.objects.filter(
            estado=True, entrenador=1, asiste=True)

        anios = []
        for pagos in EscuelaPagos.objects.all():
            if pagos.get_anio not in anios:
                anios.append(pagos.get_anio)



        pagosList = []
        for a in anios:
            for f in EscuelaFormasPago.objects.all():
                asociados_con_pagos = []
                cantidadPagos = 0
                pesos = 0
                for n in EscuelaPagos.objects.filter(formaPago=f):
                    if n.get_anio == a and n.formaPago == f.formaPago:
                        cantidadPagos += 1
                        pesos += n.get_montoAbonado
                        if n.asociado not in asociados_con_pagos:
                            asociados_con_pagos.append(n.asociado)


                pagosList.append({'anio': a,
                                  'forma': f,
                                  'cantidad': cantidadPagos,
                                  'asociados_con_pagos':len(asociados_con_pagos),
                                  'pesos': pesos})
                cantidadPagos = 0
                pesos = 0
                asociados_con_pagos = []

        context['anios'] = anios
        context['pagos_escuela'] = pagosList

        menores = 0
        intermedio = 0
        mayores = 0
        for a in Asociado.objects.filter(estado=True, entrenador=1, asiste=True):
            if a.persona.get_edad >0 and a.persona.get_edad <= 8:
                menores += 1
            elif a.persona.get_edad > 8 and a.persona.get_edad <= 12:
                intermedio += 1
            elif a.persona.get_edad > 12:
                mayores += 1

        context['menores'] = menores
        context['intermedio'] = intermedio
        context['mayores'] = mayores

        lista_x_edad = []
        for a in Asociado.objects.filter(estado=True, entrenador=1):
            lista_x_edad.append({'edad':a.persona.get_edad,'asociado':a.persona})
        context['edades'] = lista_x_edad

        context['profes'] = EscuelaAsignacTurno.objects.filter(habilitado=True, funcion=1)
        context['auxiliares'] = EscuelaAsignacTurno.objects.filter(
            habilitado=True, funcion=2)
        context['coordinador'] = EscuelaAsignacTurno.objects.filter(
            habilitado=True, funcion=3)


        return context



class PersonasList(ListView):

    model = Persona
    template_name = 'administrador/lista_personas.html'
    paginate_by =400

    ordering = ['last_name']


class SociosList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True).select_related('persona', 'tipoAsociado', 'entrenador')
    ordering = ["tipoAsociado","persona"]
    template_name = 'administrador/lista_asociados.html'



class SociosListAsamblea(ListView):
    model = Asociado
    ordering = ["persona",]
    template_name = 'administrador/lista_asociados_2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Asociado.objects.filter(estado=True).select_related('persona', 'tipoAsociado', 'entrenador').order_by("persona")


        def count_asociados_mayores_18():
            queryset = Asociado.objects.filter(estado=True).select_related('persona', 'tipoAsociado', 'entrenador')
            count = 0
            for n in queryset:
                edad = n.get_edad_persona
                if edad >= 18:
                    count += 1
            return count

        context['object_list'] = queryset
        context['count'] = count_asociados_mayores_18

        return context


class AsociadosPublicoList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True).select_related('persona', 'tipoAsociado', 'entrenador')
    ordering = ["persona",]
    template_name = 'administrador/lista_asociados_publico.html'


class AsociadosEscuelaList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(entrenador=1, estado=True).select_related('persona', 'tipoAsociado', 'entrenador')
    template_name = 'administrador/lista_escuela.html'


def _pagos_con_asociados(pagos):
    """A cada pago de socio le agrega .asociados_match (los Asociado de esa persona), armado en Python
    con 1 sola consulta. Antes el template cruzaba cada pago con TODOS los asociados (pagos x asociados
    vueltas), y eso hacia muy lentas las listas de pagos y la cuenta corriente."""
    pagos = list(pagos)
    por_persona = defaultdict(list)
    for a in Asociado.objects.select_related('persona', 'tipoAsociado'):
        por_persona[a.persona_id].append(a)
    for c in pagos:
        c.asociados_match = por_persona.get(c.personaAsociada_id, [])
    return pagos


class AsociadoPagosList(ListView):
    model = AsociadoPagos
    template_name = 'administrador/lista_pagos_socios.html'
    ordering = ['fechaPago',]

    def get_context_data(self, **kwargs):
        context = super(AsociadoPagosList, self).get_context_data(**kwargs)
        context['asociadopagos_list'] = context['object_list'] = _pagos_con_asociados(context['object_list'])
        return context


class AsociadoPagosEscuelaList(ListView):
    model = EscuelaPagos
    template_name = 'administrador/lista_pagos_escuelaAdmin.html'




class AsociadoPagosEscuelaList_mensual(ListView):
    model = EscuelaPagos
    template_name = 'administrador/listaAdmin_pagosEscuela_x_mes.html'

    def get_context_data(self, **kwargs):
        context = super(AsociadoPagosEscuelaList_mensual,
                        self).get_context_data(**kwargs)
        bonos = list(EscuelaFormasPago.objects.all())
        asociados = list(Asociado.objects.filter(estado=True, entrenador=1, asiste=True).select_related('persona'))
        # celdas de cada fila armadas aca (antes el template recorria asociados x pagos x bonos)
        celdas = defaultdict(list)
        for c in context['object_list']:
            for bono in bonos:
                if c.formaPago == bono.formaPago:
                    celdas[c.asociado_id].append(c)
        for a in asociados:
            a.pagos_celdas = celdas.get(a.id, [])
        context['bonos'] = bonos
        context['asociados'] = asociados

        return context





class AsociadoCtaCteList(ListView):
    model = AsociadoPagos
    template_name = 'administrador/cta_cte.html'

    def get_context_data(self, **kwargs):
        context = super(AsociadoCtaCteList, self).get_context_data(**kwargs)
        context['asociadopagos_list'] = context['object_list'] = _pagos_con_asociados(context['object_list'])
        return context







class EntrenadoresList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True).select_related('persona', 'tipoAsociado', 'entrenador')
    template_name = 'administrador/lista_entrenadores.html'
    ordering = ['entrenador',]

    def get_context_data(self, **kwargs):
        context = super(EntrenadoresList, self).get_context_data(**kwargs)
        context['entrenador'] = EntrenadoresKempe.objects.all()
        return context


ESTADOS_INSCRIPTOS = {
    # clave: (titulo del filtro, condicion)
    'pendientes': ('Pendientes de aprobar', Q(confirm_pago=False)),
    'aprobados': ('Aprobados sin acreditar', Q(confirm_pago=True, acreditacion=False)),
    'acreditados': ('Acreditados', Q(acreditacion=True)),
}


def _exportar_inscriptos_xlsx(evento, inscripciones):
    """Planilla Excel con los inscriptos (para cronometraje, seguro, etc.)."""
    from openpyxl import Workbook
    from openpyxl.styles import Font
    from django.http import HttpResponse
    from django.utils.text import slugify

    libro = Workbook()
    hoja = libro.active
    hoja.title = 'Inscriptos'
    columnas = ['Nº corredor', 'Nº chip', 'Apellido', 'Nombre', 'DNI', 'CUIL', 'Sexo', 'Fecha nacimiento',
                'Edad', 'Edad 31/12', 'Email', 'Teléfono', 'Ciudad', 'Modalidad', 'Distancia', 'Categoría',
                'Bici', 'Equipo', 'Grupo', 'Obra social', 'Monto abonado', 'Monto a abonar', 'Fecha pago',
                'Aprobada', 'Acreditado']
    hoja.append(columnas)
    for celda in hoja[1]:
        celda.font = Font(bold=True)
    for i in inscripciones:
        p = i.persona
        hoja.append([
            i.numero or None, i.numero_chip or None, p.last_name, p.first_name, p.dni, p.cuil, p.sexo,
            p.fechaNacimiento, i.get_edad, i.edad_31_Dic, p.email, p.telefono, p.ciudad,
            i.modalidad, i.distancia, i.categoria, i.bici, i.nombreEquipoPosta or '', i.grupo or '',
            i.obra_social, i.montoAbonado, i.montoDebeAbonar, i.fechaPago,
            'SI' if i.confirm_pago else 'NO', 'SI' if i.acreditacion else 'NO',
        ])
    for col in ('H', 'W'):
        for celda in hoja[col][1:]:
            celda.number_format = 'DD/MM/YYYY'
    for n, titulo in enumerate(columnas, start=1):
        hoja.column_dimensions[hoja.cell(row=1, column=n).column_letter].width = max(10, len(titulo) + 2)
    hoja.freeze_panes = 'A2'
    hoja.auto_filter.ref = hoja.dimensions

    respuesta = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    nombre = slugify(f'inscriptos {evento.nombreEvento} {evento.fechaEvento:%Y-%m-%d}') or 'inscriptos'
    respuesta['Content-Disposition'] = f'attachment; filename="{nombre}.xlsx"'
    libro.save(respuesta)
    return respuesta


class InscriptosList(ListView):
    model = Inscripcion
    #queryset = Inscripcion.objects.filter(confirm_pago=True)
    template_name = 'administrador/lista_inscriptos.html'

    def base(self):
        return (Inscripcion.objects.filter(eventoRelacionado=self.kwargs.get('pk'))
                .select_related('persona', 'eventoRelacionado__tipo'))

    def estado(self):
        estado = self.request.GET.get('estado', '')
        return estado if estado in ESTADOS_INSCRIPTOS else ''

    def get_queryset(self):
        qs = self.base()
        if self.estado():
            qs = qs.filter(ESTADOS_INSCRIPTOS[self.estado()][1])
        # los pendientes de aprobar primero, despues por apellido
        return qs.order_by('confirm_pago', 'persona__last_name', 'persona__first_name')

    def get(self, request, *args, **kwargs):
        if request.GET.get('exportar') == 'xlsx':
            evento = Eventos.objects.filter(pk=self.kwargs.get('pk')).first()
            if evento:
                return _exportar_inscriptos_xlsx(evento, self.get_queryset())
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(InscriptosList, self).get_context_data(**kwargs)
        filtro = self.kwargs.get('pk', None)

        cant_inscriptos_total = 0
        cant_inscriptos_f = 0
        cant_inscriptos_m = 0

        cant_inscriptos_distancia = {}
        cant_inscriptos_modalidad = {}
        cant_inscriptos_categoria = {}

        contador = 0
        contador_f = 0
        contador_m = 0

        filas = [({'distancia': x.distancia, 'modalidad': x.modalidad, 'categoria': x.categoria}, x.persona.sexo)
                 for x in Inscripcion.objects.filter(eventoRelacionado=filtro).select_related('persona')]
        cant_inscriptos_total = len(filas)
        cant_inscriptos_f = sum(1 for _, sexo in filas if sexo == 'F')
        cant_inscriptos_m = sum(1 for _, sexo in filas if sexo == 'M')
        cant_inscriptos_distancia = _tabla_por_sexo(filas, 'distancia', EventoDistancia.objects.all())
        cant_inscriptos_modalidad = _tabla_por_sexo(filas, 'modalidad', EventoModalidade.objects.all())
        cant_inscriptos_categoria = _tabla_por_sexo(filas, 'categoria', EventoCategoria.objects.all())


        formas = EventoFormasPago.objects.all()

        total = {'Total General':[cant_inscriptos_total,cant_inscriptos_f,cant_inscriptos_m]}

        modalidades = {}
        for key, value in cant_inscriptos_modalidad.items():
            modalidades.update({key:value})

        categorias = {}
        for key, value in cant_inscriptos_categoria.items():
            categorias.update({key:value})

        distancias = {}
        for key, value in cant_inscriptos_distancia.items():
            distancias.update({key:value})


        context['cant_inscriptos_total'] = cant_inscriptos_total
        context['titulos']= total
        context['modalidades'] = modalidades
        context['categorias'] = categorias
        context['distancias'] = distancias


        context['formas'] = formas
        context['eventos'] = Eventos.objects.filter(id=filtro)
        base = self.base()
        context['estado'] = self.estado()
        context['filtros_estado'] = (
            [{'clave': '', 'nombre': 'Todos', 'cantidad': base.count()}] +
            [{'clave': k, 'nombre': n, 'cantidad': base.filter(f).count()} for k, (n, f) in ESTADOS_INSCRIPTOS.items()])
        return context



class InscriptosPublicoList(ListView):
    model = Inscripcion
    queryset = (Inscripcion.objects.filter(confirm_pago=True, eventoRelacionado__publicar=True,
                                           eventoRelacionado__seguro=True, eventoRelacionado__time_control=True)
                .select_related('persona', 'eventoRelacionado__tipo'))
    template_name = 'administrador/lista_inscriptos_publico.html'

    def get_context_data(self, **kwargs):
        context = super(InscriptosPublicoList, self).get_context_data(**kwargs)


        context['eventos'] = Eventos.objects.filter(publicar=True, seguro = True, time_control = True)

        eventos = list(Eventos.objects.filter(publicar=True, seguro=True, time_control=True))
        conteo = _conteo_por_evento(eventos)
        context['inscriptos'] = {e: conteo[e]['confirmados'] if e in conteo else 0 for e in eventos}
        context['inscriptos_acreditados'] = {e: conteo[e]['acreditados'] if e in conteo else 0 for e in eventos}


        return context


class EventosList(ListView):
    model = Eventos
    template_name = 'administrador/lista_eventos.html'
    ordering = ['-fechaEvento']

    def get_context_data(self, **kwargs):
        context = super(EventosList, self).get_context_data(**kwargs)

        eventos = list(Eventos.objects.select_related('tipo'))
        conteo = _conteo_por_evento(eventos)
        context['inscriptos'] = {e: [c['total'], c['confirmados'], c['total'] - c['confirmados']]
                                 for e, c in conteo.items()}
        # tabla nueva: proximos primero (el mas cercano arriba), despues los pasados (el mas reciente arriba)
        hoy = hoy_cordoba()
        vacio = {'total': 0, 'confirmados': 0, 'acreditados': 0}
        filas = []
        for e in eventos:
            c = conteo.get(e, vacio)
            filas.append({
                'evento': e,
                'proximo': e.fechaEvento >= hoy,
                'total': c['total'],
                'aprobados': c['confirmados'],
                'pendientes': c['total'] - c['confirmados'],
                'acreditados': c['acreditados'],
                'cupo_pct': round(100 * c['total'] / e.cupo) if e.cupo else None,
            })
        proximos = sorted((f for f in filas if f['proximo']), key=lambda f: f['evento'].fechaEvento)
        pasados = sorted((f for f in filas if not f['proximo']), key=lambda f: f['evento'].fechaEvento, reverse=True)
        context['filas'] = proximos + pasados

        return context



class SeguroListAsociados(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True).select_related('persona', 'tipoAsociado', 'entrenador')
    template_name = 'seguro/lista_seguro_asociados.html'
    ordering = ['persona',]


class SeguroListEntrenadores(ListView):
    model = EntrenadoresKempe
    queryset = EntrenadoresKempe.objects.filter(seguro=True)
    template_name = 'seguro/lista_seguro_entrenadores.html'
    ordering = ['nombre', ]


class SeguroListInscriptos(ListView):
    model = Inscripcion
    queryset = (Inscripcion.objects.filter(eventoRelacionado__estado=True, eventoRelacionado__seguro=True)
                .select_related('persona', 'eventoRelacionado__tipo'))
    template_name = 'seguro/lista_seguro_eventos.html'
    ordering = ['eventoRelacionado', ]

    def get_context_data(self, **kwargs):
        context = super(SeguroListInscriptos, self).get_context_data(**kwargs)
        context['eventos'] = Eventos.objects.filter(estado=True, seguro=True)
        return context


class KempesList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True).exclude(entrenador=12).select_related('persona', 'tipoAsociado', 'entrenador')
    template_name = 'administrador/lista_kempes.html'
    ordering = ['persona', ]

class AgenciaList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True).exclude(entrenador=12).select_related('persona', 'tipoAsociado', 'entrenador')
    template_name = 'administrador/lista_agencia.html'
    ordering = ['persona', ]





def bienvenida(request):
    context = {}
    context['mensaje'] = Bienvenida.objects.all()
    return render(request, 'base/index3.html', context=context)


def adminWeb(request):
    context = {}
    return render(request, 'base/index2.html', context=context)

def ir_index2(request):
    context = {}
    return render(request, 'base/index2.html', context=context)



#def persona_editar_view(request):
    #query_dict = request.GET
    #query = query_dict.get('q')
    #persona_obj = None
    #if query is  not None:
        #persona_obj = Persona.objects.get(cuil=query)
        #if request.method == "GET":
            #form = RegistroForm(instance=persona_obj)
        #else:
            #form = RegistroForm(request.POST, instance = persona_obj)
            #if form.is_valid():
                #form.save()
                #return redirect('listado')
    #return render(request, 'usuarios/form_crear_persona.html', {"form": form})






