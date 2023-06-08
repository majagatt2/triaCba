from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin  # for create and update
from django.views.generic import ListView, CreateView, UpdateView
from apps.socio.forms import SocioForm, PagosSocioForm, EditSocioForm, PagosSocioForm_2
from apps.socio.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from datetime import date

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
    template_name = 'socio/form_asociarse_2.html'
    form_class = SocioForm
    second_form = PagosSocioForm_2
    success_url = reverse_lazy('index')
    success_message = "Gracias por Asociarte! Verifica tu estado en tu Carnet"
    
    def get_context_data(self, **kwargs):
        context = super(AsociadoCreate, self).get_context_data(**kwargs)
        if 'form' not in context:
            context['form'] = self.form_class(self.request.GET)
        if 'form2' not in context:
            context['form2'] = self.second_form(self.request.GET)
        context['entrenadores'] = EntrenadoresKempe.objects.all().order_by('nombre')
        context['tipos'] = AsociadoTipo.objects.all()
        
        formas_pago = ['Cuota Enero','Contado Enero','Cuota Febrero','Contado Febrero','Cuota Marzo','Contado Marzo','Cuota Abril','Contado Abril','Cuota Mayo','Contado Mayo','Cuota Junio','Contado Junio','Cuota Julio','Contado Julio','Cuota Agosto','Contado Agosto','Cuota Septiembre','Contado Septiembre','Cuota Octubre','Contado Octubre','Cuota Noviembre','Contado Noviembre','Cuota Diciembre','Contado Diciembre']
        costos = []
        fecha = date.today()
        mes_actual = fecha.month
        for c in AsociadoCosto.objects.all():
            if mes_actual == 1:
                if c.formaPago.formaPago == formas_pago[0] or c.formaPago.formaPago == formas_pago[1]:
                    costos.append(c)
            elif mes_actual == 2:
                if c.formaPago.formaPago == formas_pago[2] or c.formaPago.formaPago == formas_pago[3]:
                    costos.append(c)
            elif mes_actual == 3:
                if c.formaPago.formaPago == formas_pago[4] or c.formaPago.formaPago == formas_pago[5]:
                    costos.append(c)
            elif mes_actual == 4:
                if c.formaPago.formaPago == formas_pago[6] or c.formaPago.formaPago == formas_pago[7]:
                    costos.append(c)
            elif mes_actual == 5:
                if c.formaPago.formaPago == formas_pago[8] or c.formaPago.formaPago == formas_pago[9]:
                    costos.append(c)
            elif mes_actual == 6:
                if c.formaPago.formaPago == formas_pago[10] or c.formaPago.formaPago == formas_pago[11]:
                    costos.append(c)
            elif mes_actual == 7:
                if c.formaPago.formaPago == formas_pago[12] or c.formaPago.formaPago == formas_pago[13]:
                    costos.append(c)
            elif mes_actual == 8:
                if c.formaPago.formaPago == formas_pago[14] or c.formaPago.formaPago == formas_pago[15]:
                    costos.append(c)
            elif mes_actual == 9:
                if c.formaPago.formaPago == formas_pago[16] or c.formaPago.formaPago == formas_pago[17]:
                    costos.append(c)
            elif mes_actual == 10:
                if c.formaPago.formaPago == formas_pago[18] or c.formaPago.formaPago == formas_pago[19]:
                    costos.append(c)
            elif mes_actual == 11:
                if c.formaPago.formaPago == formas_pago[20] or c.formaPago.formaPago == formas_pago[21]:
                    costos.append(c)
            elif mes_actual == 12:
                if c.formaPago.formaPago == formas_pago[22] or c.formaPago.formaPago == formas_pago[23]:
                    costos.append(c)
            
                
        
        
        
        context['costos'] = costos
        return context
    
    def post(self, request, *args, **kwargs ):
        self.object = self.get_object
        form = SocioForm(request.POST, request.FILES)
        form2 = PagosSocioForm_2(request.POST, request.FILES)
        
        if form.is_valid() and form2.is_valid():
            form.instance.persona = self.request.user
            persona = form.instance.persona
            nuevo = form.save(commit=False)
            
                
            pago = form2.save(commit=False)
            pago.personaAsociada = persona
            nuevo.tipoAsociado = pago.opcionElegida.tipoSocio
            
            nuevo.save()
            pago.save()

            template = render_to_string(
                'email/alerta_admin_nuevoasociado.html', {
                    'persona': persona,
                    'fecha': nuevo.fecha,
                    'tipoAsociado': nuevo.tipoAsociado,
                    'fecha_emision_emmac': nuevo.fecha_emision_emmac,
                    'numero_emmac': nuevo.numero_emmac,
                    'con_entrenador': nuevo.con_entrenador,
                    'entrenador': nuevo.entrenador,
                    'responsable_tutor': nuevo.responsable_tutor,
                    'montoDebeAbonar': pago.montoDebeAbonar,
                    'montoAbonado': pago.montoAbonado,
                    'fechaPago': pago.fechaPago,
                    'comentario': pago.comentario,
                    
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
                    'numero_emmac': nuevo.numero_emmac,
                    'con_entrenador': nuevo.con_entrenador,
                    'entrenador': nuevo.entrenador,
                    'responsable_tutor': nuevo.responsable_tutor,
                    'montoDebeAbonar': pago.montoDebeAbonar,
                    'montoAbonado': pago.montoAbonado,
                    'fechaPago': pago.fechaPago,
                    'comentario': pago.comentario,
                })
            subject2 = f"Bienvenido {persona}"
            to_email2 = persona.email
            msg2 = EmailMessage(subject2, template2, from_email, [to_email2])
            msg2.content_subtype = "html"
            msg2.fail_silently = False
            msg2.send()
            
        else:
            return super(AsociadoCreate, self).post(request, *args, **kwargs)

        return redirect(self.get_success_url())
    

# class AsociadoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
#     model = Asociado
#     template_name = 'socio/form_asociarse.html'
#     form_class = SocioForm
#     success_url = reverse_lazy('index')
#     success_message = "Gracias por Asociarte! Verifica tu estado en tu Carnet"

#     def get_context_data(self, **kwargs):
#         context = super(AsociadoCreate, self).get_context_data(**kwargs)
#         context['entrenadores'] = EntrenadoresKempe.objects.all().order_by('nombre')
#         return context

#     def form_valid(self, form):
#         form.instance.persona = self.request.user
#         persona = form.instance.persona
#         nuevo = form.save(commit=False)
#         nuevo.save()

#         template = render_to_string(
#             'email/alerta_admin_nuevoasociado.html', {
#                 'persona': persona,
#                 'fecha': nuevo.fecha,
#                 'tipoAsociado': nuevo.tipoAsociado,
#                 'fecha_emision_emmac': nuevo.fecha_emision_emmac,
#                 'con_entrenador': nuevo.con_entrenador,
#                 'entrenador': nuevo.entrenador,
#                 'responsable_tutor': nuevo.responsable_tutor,
#             })
#         subject = f"ALERTA NUEVO ASOCIADO:  {persona}"
#         from_email = settings.EMAIL_HOST_USER
#         to_email = settings.EMAIL_HOST_USER
#         msg = EmailMessage(subject, template, from_email, [
#                            to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com'])
#         msg.content_subtype = "html"
#         msg.fail_silently = False
#         msg.send()

#         template2 = render_to_string(
#             'email/bienvenida_asociado.html', {
#                 'persona': persona,
#                 'fecha': nuevo.fecha,
#                 'tipoAsociado': nuevo.tipoAsociado,
#                 'fecha_emision_emmac': nuevo.fecha_emision_emmac,
#                 'con_entrenador': nuevo.con_entrenador,
#                 'entrenador': nuevo.entrenador,
#                 'responsable_tutor': nuevo.responsable_tutor,
#             })
#         subject2 = f"Bienvenido {persona}"
#         to_email2 = persona.email
#         msg2 = EmailMessage(subject2, template2, from_email, [to_email2])
#         msg2.content_subtype = "html"
#         msg2.fail_silently = False
#         msg2.send()

#         return super().form_valid(form)

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
        persona = form.instance.personaAsociada
        
        template = render_to_string(
            'email/alerta_admin_PagoAsociado.html', {
                'persona': persona,
                'cuota': form.instance.formaPago,
                'fechaPago': form.instance.fechaPago,
                'montoAbonado': form.instance.montoAbonado,
                'comentario': form.instance.comentario,
                

            })
        subject = f"ALERTA PAGO CUOTA ASOCIADO:  {persona}"
        from_email = settings.EMAIL_HOST_USER
        to_email = settings.EMAIL_HOST_USER
        msg = EmailMessage(subject, template, from_email, [
            to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com'])
        msg.content_subtype = "html"
        msg.fail_silently = False
        msg.send()
        
        
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
        
        formas_pago = ['Cuota Enero', 'Contado Enero', 'Cuota Febrero', 'Contado Febrero', 'Cuota Marzo', 'Contado Marzo', 'Cuota Abril', 'Contado Abril', 'Cuota Mayo', 'Contado Mayo', 'Cuota Junio', 'Contado Junio', 'Cuota Julio','Contado Julio', 'Cuota Agosto', 'Contado Agosto', 'Cuota Septiembre', 'Contado Septiembre', 'Cuota Octubre', 'Contado Octubre', 'Cuota Noviembre', 'Contado Noviembre', 'Cuota Diciembre', 'Contado Diciembre']
        costos = []
        fecha = date.today()
        mes_actual = fecha.month
        for c in AsociadoCosto.objects.all():
            if mes_actual == 1:
                if c.formaPago.formaPago == formas_pago[0]:
                    costos.append(c)
            elif mes_actual == 2:
                if c.formaPago.formaPago == formas_pago[2]:
                    costos.append(c)
            elif mes_actual == 3:
                if c.formaPago.formaPago == formas_pago[4]:
                    costos.append(c)
            elif mes_actual == 4:
                if c.formaPago.formaPago == formas_pago[6]:
                    costos.append(c)
            elif mes_actual == 5:
                if c.formaPago.formaPago == formas_pago[8]:
                    costos.append(c)
            elif mes_actual == 6:
                if c.formaPago.formaPago == formas_pago[10]:
                    costos.append(c)
            elif mes_actual == 7:
                if c.formaPago.formaPago == formas_pago[12]:
                    costos.append(c)
            elif mes_actual == 8:
                if c.formaPago.formaPago == formas_pago[14]:
                    costos.append(c)
            elif mes_actual == 9:
                if c.formaPago.formaPago == formas_pago[16]:
                    costos.append(c)
            elif mes_actual == 10:
                if c.formaPago.formaPago == formas_pago[18]:
                    costos.append(c)
            elif mes_actual == 11:
                if c.formaPago.formaPago == formas_pago[20]:
                    costos.append(c)
            elif mes_actual == 12:
                if c.formaPago.formaPago == formas_pago[22]:
                    costos.append(c)
        
        context['costos'] = costos
        
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

