from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect

from apps.inscripcion.models import EventoCosto, Inscripcion
from apps.inscripcion.forms import InscripcionForm, PersonaForm
from apps.inscripcion.models import Eventos, EventoDistancia, EventoModalidade, EventoCategoria
from apps.usuarios.models import Persona
from apps.usuarios.forms import RegistroForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin #for create and update
from django.contrib import messages #just for delete
from django.views.generic import ListView, CreateView, FormView
from django.forms.models import inlineformset_factory
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.socio.models import Asociado
from django.contrib.auth.hashers import make_password
import uuid
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string




# Create views EVENTOS - USUARIO------------------------------

def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


def listPruebas(request):
    eventos = Eventos.objects.all()
    
    return render(request, 'inscripcion/list_pruebas.html', {'eventos': eventos})



class InscripcionEventoList(ListView):
    model = Inscripcion
    template_name = 'inscripcion/lista_pagos_eventos.html'

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)
    
    
class InscripcionEventoListPublico(ListView):
    model = Inscripcion
    template_name = 'inscripcion/lista_inscriptos_publico.html'
    ordering = ['persona', ]
    
    
    def get_context_data(self, **kwargs):
        context = super(InscripcionEventoListPublico,
                        self).get_context_data(**kwargs)
        parameter = self.kwargs.get('pk', None)
        context['evento'] = Eventos.objects.filter(id=parameter)
        context['inscriptos'] = Inscripcion.objects.filter(
            eventoRelacionado=parameter)
        return context

    

    


class InscripcionEventoCreate(LoginRequiredMixin, SuccessMessageMixin,CreateView):
    model = Inscripcion
    template_name = 'inscripcion/form_inscripcion.html'
    form_class = InscripcionForm
    success_url = reverse_lazy('mis_inscripciones')
    
    def get_context_data(self, **kwargs):
        context = super(InscripcionEventoCreate, self).get_context_data(**kwargs)
        filtro = self.kwargs.get('pk', None)
        context['eventos'] = Eventos.objects.filter(id=filtro)
        context['costos'] = EventoCosto.objects.filter(evento=filtro)
        asociados = Asociado.objects.filter(persona=self.request.user)
        lista = []
        for asociado in asociados:
            lista.append(asociado)
        context['asociado'] = lista
        # context['distancia'] = EventoDistancia.objects.all()
        # context['categoria'] = EventoCategoria.objects.all()
        return context
    

    def form_valid(self, form, **kwargs):
        form.instance.persona = self.request.user
        persona = form.instance.persona
        nuevo = form.save(commit=False)
        nuevo.save()
        
        template = render_to_string(
            'email/alerta_admin_nuevoinscripto.html', {
                'persona': persona,
                'eventoRelacionado': nuevo.eventoRelacionado,
                'distancia': nuevo.distancia,
                'categoria': nuevo.categoria,
                'bici': nuevo.bici,
                'nombreEquipoPosta': nuevo.nombreEquipoPosta,
                'montoDebeAbonar': nuevo.montoDebeAbonar,
                'montoAbonado': nuevo.montoAbonado,
                'fechaPago': nuevo.fechaPago,
                'comentario': nuevo.comentario,
                'obra_social': nuevo.obra_social,
                'responsable_tutor': nuevo.responsable_tutor,
                'relacion_legal': nuevo.relacion_legal,
                'dni_responsable': nuevo.dni_responsable,
                'mail_responsable': nuevo.mail_responsable,
                'telefono_responsable': nuevo.telefono_responsable,
                
            })
        subject = f"ALERTA NUEVO INSCRIPTO:  {persona} - {nuevo.eventoRelacionado}"
        from_email = settings.EMAIL_HOST_USER
        to_email = settings.EMAIL_HOST_USER
        msg = EmailMessage(subject, template, from_email, [
                           to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com'])
        msg.content_subtype = "html"
        msg.fail_silently = False
        msg.send()
        
        template2 = render_to_string(
            'email/bienvenida_inscripto.html', {
                'persona': persona,
                'username':persona.username,
                'email':persona.email,
                'eventoRelacionado': nuevo.eventoRelacionado,
                'distancia': nuevo.distancia,
                'categoria': nuevo.categoria,
                'bici': nuevo.bici,
                'nombreEquipoPosta': nuevo.nombreEquipoPosta,
                'montoDebeAbonar': nuevo.montoDebeAbonar,
                'montoAbonado': nuevo.montoAbonado,
                'fechaPago': nuevo.fechaPago,
                'comentario': nuevo.comentario,
                'obra_social': nuevo.obra_social,
                'responsable_tutor': nuevo.responsable_tutor,
                'relacion_legal': nuevo.relacion_legal,
                'dni_responsable': nuevo.dni_responsable,
                'mail_responsable': nuevo.mail_responsable,
                'telefono_responsable': nuevo.telefono_responsable,
            })
        subject2 = f"Gracias {persona} por inscribirte en {nuevo.eventoRelacionado}"
        to_email2 = persona.email
        msg2 = EmailMessage(subject2, template2, from_email, [to_email2])
        msg2.content_subtype = "html"
        msg2.fail_silently = False
        msg2.send()
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        return super().form_valid(form)
    
   
    success_message = "Gracias por Inscribirte! Verifica el estado de tu inscripción"
    

    
class InscripcionPublicoEventoCreate(SuccessMessageMixin, CreateView):
    model = Persona
    template_name = 'inscripcion/form_inscripcion_publico.html'
    form_class = PersonaForm
    second_form = InscripcionForm
    success_url = reverse_lazy('eventos_publico')
    success_message = "Thank You for registering!"

    def get_context_data(self, **kwargs):
        context = super(InscripcionPublicoEventoCreate,self).get_context_data(**kwargs)
        filtro = self.kwargs.get('pk', None)
        context['eventos'] = Eventos.objects.filter(id=filtro)
        context['costos'] = EventoCosto.objects.filter(evento=filtro)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        if 'form2' not in context:
            context['form2'] = self.second_form(self.request.GET)
        return context
    
  
    def post(self, request, *args, **kwargs ):
        self.object = self.get_object
        form = PersonaForm(request.POST, request.FILES)
        form2 = InscripcionForm(request.POST, request.FILES)
        
        if form.is_valid() and form2.is_valid():
            persona = form.save(commit=False)
            nuevo = form2.save(commit=False)
            persona.password = make_password('sin password')
            persona.username = uuid.uuid4().hex[:9]
            persona.save()
            nuevo.persona = persona
            nuevo.save()
            
            # template = render_to_string(
            #     'email/alerta_admin_nuevoinscripto.html', {
            #         'persona': persona,
            #         'eventoRelacionado': nuevo.eventoRelacionado,
            #         'distancia': nuevo.distancia,
            #         'categoria': nuevo.categoria,
            #         'bici': nuevo.bici,
            #         'nombreEquipoPosta': nuevo.nombreEquipoPosta,
            #         'montoDebeAbonar': nuevo.montoDebeAbonar,
            #         'montoAbonado': nuevo.montoAbonado,
            #         'fechaPago': nuevo.fechaPago,
            #         'comentario': nuevo.comentario,
            #         'obra_social': nuevo.obra_social,
            #         'responsable_tutor': nuevo.responsable_tutor,
            #         'relacion_legal': nuevo.relacion_legal,
            #         'dni_responsable': nuevo.dni_responsable,
            #         'mail_responsable': nuevo.mail_responsable,
            #         'telefono_responsable': nuevo.telefono_responsable,

            #     })
            # subject = f"ALERTA NUEVO INSCRIPTO:  {persona} - {nuevo.eventoRelacionado}"
            # from_email = settings.EMAIL_HOST_USER
            # to_email = settings.EMAIL_HOST_USER
            # msg = EmailMessage(subject, template, from_email, [
            #                 to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com'])
            # msg.content_subtype = "html"
            # msg.fail_silently = False
            # msg.send()

            # template2 = render_to_string(
            #     'email/bienvenida_inscripto.html', {
            #         'persona': persona,
            #         'username': persona.username,
            #         'email': persona.email,
            #         'eventoRelacionado': nuevo.eventoRelacionado,
            #         'distancia': nuevo.distancia,
            #         'categoria': nuevo.categoria,
            #         'bici': nuevo.bici,
            #         'nombreEquipoPosta': nuevo.nombreEquipoPosta,
            #         'montoDebeAbonar': nuevo.montoDebeAbonar,
            #         'montoAbonado': nuevo.montoAbonado,
            #         'fechaPago': nuevo.fechaPago,
            #         'comentario': nuevo.comentario,
            #         'obra_social': nuevo.obra_social,
            #         'responsable_tutor': nuevo.responsable_tutor,
            #         'relacion_legal': nuevo.relacion_legal,
            #         'dni_responsable': nuevo.dni_responsable,
            #         'mail_responsable': nuevo.mail_responsable,
            #         'telefono_responsable': nuevo.telefono_responsable,
            #     })
            # subject2 = f"Gracias {persona} por inscribirte en {nuevo.eventoRelacionado}"
            # to_email2 = persona.email
            # msg2 = EmailMessage(subject2, template2, from_email, [to_email2])
            # msg2.content_subtype = "html"
            # msg2.fail_silently = False
            # msg2.send()

            
        else:
            #print(form.errors)
            return super(InscripcionPublicoEventoCreate, self).post(request, *args, **kwargs)
        
        return redirect(self.get_success_url())




class InscripcionEventoUsuarioList(ListView):
    model = Inscripcion
    template_name = 'inscripcion/lista_pagos_Eventos.html'

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)
    
    
class EventosList(ListView):
    model = Eventos
    queryset = Eventos.objects.filter(estado=True)
    template_name = 'inscripcion/eventos.html'

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)
    

class EventosPublicoList(ListView):
    model = Eventos
    queryset = Eventos.objects.filter(estado=True)
    template_name = 'inscripcion/eventos_publico.html'
    
    
class EventosListDetalles(ListView):
    model = Eventos
    template_name = 'inscripcion/detalle_evento.html'
    
   
    def get_context_data(self, **kwargs):
        context = super(EventosListDetalles, self).get_context_data(**kwargs)
        parametro = self.kwargs.get('parametro', None)
        context['eventos'] = Eventos.objects.filter(id=parametro)
        return context

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)
    
    
