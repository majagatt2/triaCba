from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin  # for create and update
from django.views.generic import ListView, CreateView, UpdateView
from apps.socio.forms import SocioForm, PagosSocioForm, EditSocioForm
from apps.socio.models import *
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail, mail_admins, EmailMultiAlternatives, EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from datetime import date

# Create views SOCIOS - ADMINISTRADOR #.


def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html', status=404)


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
        asociados = Asociado.objects.filter(persona=self.request.user).order_by('id')
        lista = []
        for asociado in asociados:
            lista.append(asociado)

        context['asociado'] = lista
        context['requisitos']= AsociadoRequisitos.objects.all()
        if lista:
            ultimo = lista[-1]
            context.update(datos_carnet(ultimo))
            context['asociado'] = lista
            context['carnet'] = ultimo
            context['ahora'] = ahora_cordoba()
            context['ahora_ms'] = int(timezone.now().timestamp() * 1000)
            token = signing.dumps(ultimo.pk, salt=SALT_CARNET)
            context['url_verificacion'] = self.request.build_absolute_uri(reverse('verificar_carnet', args=[token]))
        return context


class AsociadoCreate(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Asociado
    template_name = 'socio/form_asociarse.html'
    form_class = SocioForm
    second_form = PagosSocioForm
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
                if c.formaPago.formaPago == formas_pago[1]:
                    costos.append(c)
            elif mes_actual == 2:
                if c.formaPago.formaPago == formas_pago[3]:
                    costos.append(c)
            elif mes_actual == 3:
                if c.formaPago.formaPago == formas_pago[5]:
                    costos.append(c)
            elif mes_actual == 4:
                if c.formaPago.formaPago == formas_pago[7]:
                    costos.append(c)
            elif mes_actual == 5:
                if c.formaPago.formaPago == formas_pago[9]:
                    costos.append(c)
            elif mes_actual == 6:
                if c.formaPago.formaPago == formas_pago[11]:
                    costos.append(c)
            elif mes_actual == 7:
                if c.formaPago.formaPago == formas_pago[13]:
                    costos.append(c)
            elif mes_actual == 8:
                if  c.formaPago.formaPago == formas_pago[15]:
                    costos.append(c)
            elif mes_actual == 9:
                if c.formaPago.formaPago == formas_pago[17]:
                    costos.append(c)
            elif mes_actual == 10:
                if c.formaPago.formaPago == formas_pago[19]:
                    costos.append(c)
            elif mes_actual == 11:
                if  c.formaPago.formaPago == formas_pago[21]:
                    costos.append(c)
            elif mes_actual == 12:
                if  c.formaPago.formaPago == formas_pago[23]:
                    costos.append(c)





        context['costos'] = costos
        return context

    def post(self, request, *args, **kwargs ):
        self.object = self.get_object
        form = SocioForm(request.POST, request.FILES)
        form2 = PagosSocioForm(request.POST, request.FILES)

        if form.is_valid() and form2.is_valid():
            form.instance.persona = self.request.user
            if form.instance.fecha_emision_emmac == None:
                form.instance.fecha_emision_emmac = '2000-01-01'
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
                            to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com','admtriacba@gmail.com'])
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
            return render(request, 'socio/form_asociarse.html', {'form': form,'form2': form2})
            #return super(AsociadoCreate, self).post(request, *args, **kwargs)

        return redirect(self.get_success_url())



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
            to_email, 'triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com','admtriacba@gmail.com'])
        msg.content_subtype = "html"
        msg.fail_silently = False
        msg.send()




        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super(AsociadoPagoCreate,
                        self).get_context_data(**kwargs)
        asociados = Asociado.objects.filter(persona=self.request.user).order_by('id')
        lista = []
        for asociado in asociados:
            lista.append(asociado)
        context['asociado'] = lista
        context['tipos'] = AsociadoTipo.objects.all()
        formas_pago = ['Cuota/s Adeudada/s','Cambio Condición Asociativa', 'Compras Varias']
        costos = []
        fecha = date.today()
        mes_actual = fecha.month
        for c in AsociadoCosto.objects.all():
            if c.formaPago.formaPago == formas_pago[0]:
                    costos.append(c)
            if c.formaPago.formaPago == formas_pago[1]:
                    costos.append(c)
            if c.formaPago.formaPago == formas_pago[2]:
                    costos.append(c)

        context['costos'] = costos
        return context



class AsociadoPagosList(ListView):
    model = AsociadoPagos
    template_name = 'socio/lista_pagos_socio.html'


    def form_valid(self, form):
        form.instance.personaAsociada = self.request.user
        return super().form_valid(form)


def mensaje(request):
    return render(request, 'socio/mensaje_pago.html')


# ---------- Carnet digital ----------

from django.core import signing
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils import timezone
from zoneinfo import ZoneInfo

ZONA_CORDOBA = ZoneInfo('America/Argentina/Cordoba')
SALT_CARNET = 'carnet-federado'


def _dni_con_puntos(dni):
    digitos = ''.join(c for c in str(dni or '') if c.isdigit())
    if not digitos:
        return ''
    return f"{int(digitos):,}".replace(',', '.')


def datos_carnet(asociado):
    """Todo lo que muestra el carnet (y la pagina de verificacion) sobre un asociado."""
    hoy = date.today()
    vencimiento = asociado.get_vencimiento
    vigente = vencimiento >= hoy
    if not vigente:
        estado, estado_texto = 'vencido', 'Vencido'
    elif not asociado.estado:
        estado, estado_texto = 'pendiente', 'Pendiente de activación'
    else:
        estado, estado_texto = 'vigente', 'Vigente'
    emmac_presentado = bool(asociado.fecha_emision_emmac) and not asociado.get_emmac_no_presentado
    persona = asociado.persona
    foto = ''
    if persona.fotoPerfil and 'Default_1234' not in persona.fotoPerfil.name:
        foto = persona.fotoPerfil.url
    return {
        'asociado': asociado,
        'persona': persona,
        'foto': foto,
        'iniciales': ((persona.first_name or ' ')[0] + (persona.last_name or ' ')[0]).strip().upper(),
        'dni': _dni_con_puntos(persona.dni),
        'estado': estado,
        'estado_texto': estado_texto,
        'vencimiento': vencimiento,
        'emmac_ok': emmac_presentado and asociado.get_sit_emmac,
        'emmac_presentado': emmac_presentado,
        'emmac_vencimiento': asociado.get_vencimiento_emmac if emmac_presentado else None,
    }


def ahora_cordoba():
    return timezone.localtime(timezone.now(), ZONA_CORDOBA)


def verificar_carnet(request, token):
    """Pagina publica que abre el QR del carnet: muestra la situacion REAL al momento de escanear."""
    try:
        asociado_id = signing.loads(token, salt=SALT_CARNET)
    except signing.BadSignature:
        return render(request, 'socio/verificar_carnet.html', {'invalido': True, 'ahora': ahora_cordoba()}, status=404)
    asociado = get_object_or_404(Asociado.objects.select_related('persona', 'tipoAsociado', 'entrenador'), pk=asociado_id)
    # si la persona se volvio a asociar, vale el registro mas nuevo
    ultimo = Asociado.objects.filter(persona=asociado.persona).select_related('persona', 'tipoAsociado', 'entrenador').order_by('id').last()
    contexto = datos_carnet(ultimo or asociado)
    contexto['ahora'] = ahora_cordoba()
    respuesta = render(request, 'socio/verificar_carnet.html', contexto)
    respuesta['X-Robots-Tag'] = 'noindex, nofollow'
    respuesta['Cache-Control'] = 'no-store'
    return respuesta
