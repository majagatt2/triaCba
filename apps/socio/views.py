from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin  # for create and update
from django.views.generic import ListView, CreateView, UpdateView
from apps.socio.forms import SocioForm, PagosSocioForm, EditSocioForm
from apps.socio.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string

# Create views SOCIOS - ADMINISTRADOR #.


def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


class AsociadosList(ListView):
    model = Asociado
    template_name = 'administrador/lista_asociados.html'

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)


class AsociadoCertifList(ListView):
    model = Asociado
    template_name = 'socio/asociado_carnet.html'

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(AsociadoCertifList, self).get_context_data(**kwargs)
        asociados = Asociado.objects.filter(persona=self.request.user)
        lista = []
        for asociado in asociados:
            lista.append(asociado)
        context['asociado'] = lista
        context['requisitos']= AsociadoRequisitos.objects.all()
        return context
    

class AsociadoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Asociado
    template_name = 'socio/form_asociarse.html'
    form_class = SocioForm
    success_url = reverse_lazy('index')
    success_message = "Gracias por Asociarte! Verifica tu estado en tu Carnet"
    
    def form_valid(self, form):
        form.instance.persona = self.request.user
        persona = form.instance.persona
        nuevo = form.save(commit=False)
        nuevo.save()

        template = render_to_string(
            'email/alerta_admin_nuevoasociado.html', {
                'persona': persona,
                'fecha': nuevo.fecha,
                'tipoAsociado': nuevo.tipoAsociado,
                'fecha_emision_emmac': nuevo.fecha_emision_emmac,
                'con_entrenador': nuevo.con_entrenador,
                'entrenador': nuevo.entrenador,
                'responsable_tutor': nuevo.responsable_tutor,
            })
        subject = f"ALERTA NUEVO ASOCIADO:  {persona}"
        from_email = settings.EMAIL_HOST_USER
        to_email = settings.EMAIL_HOST_USER
        msg = EmailMessage(subject, template, from_email, [
                           to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com'])
        msg.content_subtype = "html"
        msg.fail_silently = False
        msg.send()

        template2 = render_to_string(
            'email/bienvenida_asociado.html', {
                'persona': persona,
                'fecha': nuevo.fecha,
                'tipoAsociado': nuevo.tipoAsociado,
                'fecha_emision_emmac': nuevo.fecha_emision_emmac,
                'con_entrenador': nuevo.con_entrenador,
                'entrenador': nuevo.entrenador,
                'responsable_tutor': nuevo.responsable_tutor,
            })
        subject2 = f"Bienvenido {persona}"
        to_email2 = persona.email
        msg2 = EmailMessage(subject2, template2, from_email, [to_email2])
        msg2.content_subtype = "html"
        msg2.fail_silently = False
        msg2.send()

        return super().form_valid(form)
    
    

class AsociadoEditar(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Asociado
    
    template_name = 'socio/asociado_editar.html'
    form_class = EditSocioForm
    success_url = reverse_lazy('carnet')
    success_message = "La información se modificó con éxito"
    
    def form_valid(self, form):
        form.instance.asociado = self.request.user
        return super().form_valid(form)
    
    
class AsociadoPagoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = AsociadoPagos
    template_name = 'socio/form_pago_socios.html'
    form_class = PagosSocioForm
    success_url = reverse_lazy('lista_pagos_socio')
    success_message = "Hemos registrado tu pago! Lo estamos procesando"

    def form_valid(self, form):
        form.instance.personaAsociada = self.request.user
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super(AsociadoPagoCreate,
                        self).get_context_data(**kwargs)
        asociados = Asociado.objects.filter(persona=self.request.user)
        lista = []
        for asociado in asociados:
            lista.append(asociado)
        context['asociado'] = lista
        context['tipos'] = AsociadoTipo.objects.all()
        context['costos'] = AsociadoCosto.objects.all()
        return context

    
    
class AsociadoPagosList(ListView):
    model = AsociadoPagos
    template_name = 'socio/lista_pagos_socio.html'
    ordering= ['fechaPago',]

    def form_valid(self, form):
        form.instance.personaAsociada = self.request.user
        return super().form_valid(form)


def mensaje(request):
    return render(request,'mensaje')

