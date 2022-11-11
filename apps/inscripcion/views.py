from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from apps.inscripcion.models import EventoCosto, Inscripcion
from apps.inscripcion.forms import InscripcionForm, EventosForm
from apps.inscripcion.models import Eventos, EventoDistancia, EventoModalidade, EventoCategoria
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin #for create and update
from django.contrib import messages #just for delete
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.socio.models import Asociado


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
        form.save()
        return super().form_valid(form)
    
   
    success_message = "Gracias por Inscribirte! Verifica el estado de tu inscripción"
    
    

        





    
  
        

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
    
    
