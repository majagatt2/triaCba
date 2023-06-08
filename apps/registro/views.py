
from apps.registro.models import Bienvenida
from apps.usuarios.forms import RegistroForm
from apps.usuarios.models import  Persona
from apps.inscripcion.models import EventoCategoria, Eventos
from apps.inscripcion.models import Inscripcion
from apps.socio.models import Asociado, AsociadoPagos, AsociadoTipo, EntrenadoresKempe
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from apps.escuela.models import EscuelaPagos, EscuelaFormasPago,EscuelaAsignacTurno

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect



# Create your views here.

# def login(request):
#     return render(request, 'registration/login.html')


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
            if e.id != 1 and e.id != 12: #1 es Escuela y 12 es Sin Entrenador
                total_atletas_con_entrenador += Asociado.objects.filter(
                estado=True, entrenador=e.id).count()
                if Asociado.objects.filter(
                    estado=True, entrenador=e.id).count() > 0:
                    entrenadores_con_atletas += 1
            
        context['atletas_x_entrenador'] = atletas_x_entrenador
        context['entrenadores'] = entrenadores_con_atletas
        context['con_acceso_kempes'] = total_atletas_con_entrenador
        
        evento = {}
        for e in Eventos.objects.filter(estado=True):
            inscriptos = 0
            inscriptos_confirmados = 0
            for i in Inscripcion.objects.filter(eventoRelacionado=e):
                inscriptos += Inscripcion.objects.filter(eventoRelacionado=e).count()
                inscriptos_confirmados += Inscripcion.objects.filter(eventoRelacionado=e,confirm_pago=True).count()
                evento.update({e:[inscriptos,inscriptos_confirmados]})
                inscriptos = 0
                inscriptos_confirmados = 0
                
        atletas_x_categoria = {}
        
        for event in Eventos.objects.filter(estado=True):
            for categoria in EventoCategoria.objects.all():
                cuenta = 0
                cuenta += Inscripcion.objects.filter(
                    confirm_pago=True, categoria=categoria).count()
                
                atletas_x_categoria.update({categoria:cuenta})
                cuenta = 0
    
        context['eventos'] = evento
        context['atletas_x_categoria'] = atletas_x_categoria
        
        
       
        anios=[]
        for pagos in EscuelaPagos.objects.all():
            if pagos.get_anio not in anios:
                anios.append(pagos.get_anio)
                
        pagosList = []
        for a in anios:
            for f in EscuelaFormasPago.objects.all():
                cantidadPagos = 0
                pesos = 0
                for n in EscuelaPagos.objects.filter(formaPago=f):
                    if n.get_anio == a and n.formaPago == f.formaPago:
                        cantidadPagos += 1
                        pesos += n.get_montoAbonado
                   
                pagosList.append({'anio':a,
                                  'forma':f,
                                  'cantidad':cantidadPagos, 
                                  'pesos':pesos})
                cantidadPagos = 0
                pesos = 0
                                
                            
        context['anios'] = anios
        context['pagos_escuela'] = pagosList
        context['formas_pago'] = EscuelaFormasPago.objects.all()
        
        
        
        
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
        
        context['profes'] = EscuelaAsignacTurno.objects.filter(habilitado=True, funcion=2)
        context['auxiliares'] = EscuelaAsignacTurno.objects.filter(
            habilitado=True, funcion=3)
        context['coordinador'] = EscuelaAsignacTurno.objects.filter(
            habilitado=True, funcion=4)


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


class AsociadosPublicoList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True)
    ordering = ["persona", ]
    template_name = 'administrador/lista_asociados_publico.html'



class AsociadosEscuelaList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(tipoAsociado=5, estado=True)
    template_name = 'administrador/lista_escuela.html'


class AsociadoPagosList(ListView):
    model = AsociadoPagos
    template_name = 'administrador/lista_pagos_socios.html'


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
    
    def get_context_data(self, **kwargs):
        context = super(InscriptosList, self).get_context_data(**kwargs)
        
        cant_inscriptos = 0
        for x in Eventos.objects.filter(estado = True):
            cant_inscriptos += Inscripcion.objects.filter(eventoRelacionado=x.id).count()
                 
                
        context['cantidad_inscriptos']= cant_inscriptos    
        
        
        context['eventos'] = Eventos.objects.filter(estado=True)
        return context
    

class InscriptosPublicoList(ListView):
    model = Inscripcion
    queryset = Inscripcion.objects.filter(confirm_pago=True)
    template_name = 'administrador/lista_inscriptos_publico.html'

    def get_context_data(self, **kwargs):
        context = super(InscriptosPublicoList, self).get_context_data(**kwargs)
        context['eventos'] = Eventos.objects.filter(publicar=True)
        return context

    
class EventosList(ListView):
    model = Eventos
    template_name = 'administrador/lista_eventos.html'    
    ordering = ['-fechaEvento']
   
   
class SeguroListAsociados(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True)
    template_name = 'seguro/lista_seguro_asociados.html'
    ordering = ['persona',]
    

class SeguroListEntrenadores(ListView):
    model = EntrenadoresKempe
    queryset = EntrenadoresKempe.objects.filter(habilitado=True)
    template_name = 'seguro/lista_seguro_entrenadores.html'
    ordering = ['nombre', ]
   

class SeguroListInscriptos(ListView):
    model = Inscripcion
    queryset = Inscripcion.objects.all()
    template_name = 'seguro/lista_seguro_eventos.html'
    ordering = ['eventoRelacionado', ]
    
    def get_context_data(self, **kwargs):
        context = super(SeguroListInscriptos, self).get_context_data(**kwargs)
        context['eventos'] = Eventos.objects.filter(estado=True, seguro=True)
        return context


class KempesList(ListView):
    model = Asociado
    queryset = Asociado.objects.filter(estado=True,).exclude(entrenador=12)
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




# def persona_editar_view(request):
#     query_dict = request.GET
#     query = query_dict.get('q')
#     persona_obj = None
#     if query is  not None:
#         persona_obj = Persona.objects.get(cuil=query)
#         if request.method == "GET":
#             form = RegistroForm(instance=persona_obj)
#         else:
#             form = RegistroForm(request.POST, instance = persona_obj)
#             if form.is_valid():
#                 form.save()
#                 return redirect('listado')
#     return render(request, 'usuarios/form_crear_persona.html', {"form": form})





    
