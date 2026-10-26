
from apps.registro.models import Bienvenida
from apps.usuarios.forms import RegistroForm
from apps.usuarios.models import  Persona
from apps.inscripcion.models import Eventos, EventoCosto, EventoDistancia, EventoModalidade, EventoCategoria, EventoFormasPago
from apps.inscripcion.models import Inscripcion
from apps.socio.models import Asociado, AsociadoPagos, AsociadoTipo, EntrenadoresKempe
from django.views.generic import ListView
#from django.urls import reverse_lazy
from apps.escuela.models import EscuelaPagos, EscuelaFormasPago,EscuelaAsignacTurno


#from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from collections import Counter
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
    queryset = Asociado.objects.filter(estado=True)
    ordering = ["tipoAsociado","persona"]
    template_name = 'administrador/lista_asociados.html'



class SociosListAsamblea(ListView):
    model = Asociado
    ordering = ["persona",]
    template_name = 'administrador/lista_asociados_2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = Asociado.objects.filter(estado=True).order_by("persona")


        def count_asociados_mayores_18():
            queryset = Asociado.objects.filter(estado=True)
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
    queryset = Asociado.objects.filter(estado=True)
    ordering = ["persona",]
    template_name = 'administrador/lista_asociados_publico.html'


class AsociadosEscuelaList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(entrenador=1, estado=True)
    template_name = 'administrador/lista_escuela.html'


class AsociadoPagosList(ListView):
    model = AsociadoPagos
    template_name = 'administrador/lista_pagos_socios.html'
    ordering = ['fechaPago',]

    def get_context_data(self, **kwargs):
        context = super(AsociadoPagosList, self).get_context_data(**kwargs)
        context['asociados_todos'] = Asociado.objects.all()
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
        context['bonos'] = EscuelaFormasPago.objects.all()
        context['asociados'] = Asociado.objects.filter(estado=True, entrenador=1,asiste=True)

        return context





class AsociadoCtaCteList(ListView):
    model = AsociadoPagos
    template_name = 'administrador/cta_cte.html'

    def get_context_data(self, **kwargs):
        context = super(AsociadoCtaCteList, self).get_context_data(**kwargs)
        context['asociados_todos'] = Asociado.objects.all()
        return context







class EntrenadoresList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True)
    template_name = 'administrador/lista_entrenadores.html'
    ordering = ['entrenador',]

    def get_context_data(self, **kwargs):
        context = super(EntrenadoresList, self).get_context_data(**kwargs)
        context['entrenador'] = EntrenadoresKempe.objects.all()
        return context


class InscriptosList(ListView):
    model = Inscripcion
    #queryset = Inscripcion.objects.filter(confirm_pago=True)
    template_name = 'administrador/lista_inscriptos.html'

    def get_queryset(self):
        return (Inscripcion.objects.filter(eventoRelacionado=self.kwargs.get('pk'))
                .select_related('persona', 'eventoRelacionado__tipo'))

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

        conteo = _conteo_por_evento(list(Eventos.objects.select_related('tipo')))
        context['inscriptos'] = {e: [c['total'], c['confirmados'], c['total'] - c['confirmados']]
                                 for e, c in conteo.items()}

        return context



class SeguroListAsociados(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True)
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
    queryset = Asociado.objects.filter(estado=True).exclude(entrenador=12)
    template_name = 'administrador/lista_kempes.html'
    ordering = ['persona', ]

class AgenciaList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True).exclude(entrenador=12)
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






