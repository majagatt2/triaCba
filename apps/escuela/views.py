from django.shortcuts import render
from apps.escuela.models import *
from django.views.generic import ListView, CreateView
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin  # for create and update
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from apps.escuela.forms import EscuelaPagosForm, AsistenciaForm



# Create your views here.


class EscuelaPagoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = EscuelaPagos
    template_name = 'escuela/form_pago_escuela.html'
    form_class = EscuelaPagosForm
    success_url = reverse_lazy('lista_pagos_escuela')
    success_message = "Hemos registrado tu pago! Lo estamos procesando"

    def get_context_data(self, **kwargs):
        context = super(EscuelaPagoCreate,
                        self).get_context_data(**kwargs)
        asociados = Asociado.objects.filter(persona=self.request.user)
        lista = []
        for asociado in asociados:
            lista.append(asociado)
        context['asociado'] = lista
        context['tipos'] = EscuelaFormasPago.objects.all()
        context['costos'] = EscuelaCosto.objects.all()
        return context
   
    
    def form_valid(self, form):
        asociados = Asociado.objects.filter(persona=self.request.user)
        lista = []
        for asociado in asociados:
            lista.append(asociado)
        form.instance.asociado = lista[-1]
        nuevo_pago = form.save(commit=False)
        asociado = form.instance.asociado
        nuevo_pago.save()
        
        template = render_to_string(
            'email/alerta_admin_PagoEscuela.html', {
                'asociado': asociado,
                'opcion_elegida': nuevo_pago.opcionElegida,
                'tipoAsociado': nuevo_pago.tipoPago,
                'vencimiento': asociado.get_vencimiento,
                'cuota': nuevo_pago.formaPago,
                'monto_debe_abonar':nuevo_pago.montoDebeAbonar,
                'monto_abonado': nuevo_pago.montoAbonado,
                'fecha_pago': nuevo_pago.fechaPago,
                'comentario': nuevo_pago.comentario,
            })
        subject = f"ALERTA NUEVO PAGO ESCUELA:  {asociado}"
        from_email = settings.EMAIL_HOST_USER
        to_email = settings.EMAIL_HOST_USER
        msg = EmailMessage(subject, template, from_email, [
                           to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com', 'carolinamonasterolo@gmail.com'])
        msg.content_subtype = "html"
        msg.fail_silently = False
        msg.send()

        
        
        
        
        
        return super().form_valid(form)

    


class EscuelaPagosList(ListView):
    model = EscuelaPagos
    template_name = 'escuela/lista_pagos_escuela.html'
    ordering = ['fechaPago', ]

    # def form_valid(self, form):
    #     form.instance.asociado = self.request.user
    #     return super().form_valid(form)

class EscuelaAsistenciaCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model=EscuelaAsistencia
    queryset = Asociado.objects.filter(estado=True, tipoAsociado=5)
    template_name='escuela/form_asistencia.html'
    form_class=AsistenciaForm
    success_url=reverse_lazy('asistencia')
    success_message="Se han guardado los cambios"

    def get_context_data(self, **kwargs):
        context = super(EscuelaAsistenciaCreate,
                        self).get_context_data(**kwargs)
        context['asociados'] = Asociado.objects.filter(
            estado=True, tipoAsociado=5)
        return context
