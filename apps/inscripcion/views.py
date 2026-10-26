from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from apps.inscripcion.models import EventoCosto, Inscripcion, ModalidadEventos
from apps.inscripcion.forms import InscripcionForm, EventosForm, PersonaForm
from apps.inscripcion.models import Eventos, EventoDistancia, EventoModalidade, EventoCategoria
from apps.usuarios.models import Persona
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.messages.views import SuccessMessageMixin #for create and update
from django.contrib import messages #just for delete
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.socio.models import Asociado
from django.contrib.auth.hashers import make_password
import uuid
import secrets
from django.core.mail import EmailMessage
from django.conf import settings
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

def edad_al(fecha_nacimiento, fecha):
    """Edad que tiene la persona en una fecha (la del evento)."""
    if not fecha_nacimiento or not fecha:
        return None
    return fecha.year - fecha_nacimiento.year - ((fecha.month, fecha.day) < (fecha_nacimiento.month, fecha_nacimiento.day))


def faltan_datos_menor(form):
    """Para menores de 18: los datos del adulto responsable son obligatorios. Marca los que faltan."""
    datos = form.cleaned_data
    faltan = False
    if not (datos.get('responsable_tutor') or '').strip():
        form.add_error('responsable_tutor', 'Completá el nombre y apellido de tu madre, padre o tutor.'); faltan = True
    if datos.get('relacion_legal') in (None, '', '1'):
        form.add_error('relacion_legal', 'Elegí qué relación tiene con vos.'); faltan = True
    if not datos.get('dni_responsable'):
        form.add_error('dni_responsable', 'Completá el DNI del adulto responsable.'); faltan = True
    if not (datos.get('telefono_responsable') or '').strip():
        form.add_error('telefono_responsable', 'Completá un teléfono del adulto responsable.'); faltan = True
    return faltan


DESTINATARIOS_ADMIN = ['triatloncba@gmail.com', 'triatloncba.infantojuvenil@gmail.com', 'admtriacba@gmail.com']


def enviar_emails_inscripcion(persona, nuevo, password=None):
    """Envia el aviso a la asociacion y la confirmacion al atleta.

    La inscripcion ya esta guardada cuando se llama: si Gmail falla, se registra el error
    y se devuelve False, pero el atleta NO ve una pagina de error.
    """
    datos = {
        'persona': persona, 'username': persona.username, 'email': persona.email,
        'eventoRelacionado': nuevo.eventoRelacionado, 'distancia': nuevo.distancia,
        'categoria': nuevo.categoria, 'bici': nuevo.bici, 'nombreEquipoPosta': nuevo.nombreEquipoPosta,
        'montoDebeAbonar': nuevo.montoDebeAbonar, 'montoAbonado': nuevo.montoAbonado,
        'fechaPago': nuevo.fechaPago, 'comentario': nuevo.comentario, 'obra_social': nuevo.obra_social,
        'responsable_tutor': nuevo.responsable_tutor, 'relacion_legal': nuevo.relacion_legal,
        'dni_responsable': nuevo.dni_responsable, 'mail_responsable': nuevo.mail_responsable,
        'telefono_responsable': nuevo.telefono_responsable,
        'password': password,
    }
    from_email = settings.EMAIL_HOST_USER
    ok = True
    try:
        msg = EmailMessage(
            f"ALERTA NUEVO INSCRIPTO:  {persona} - {nuevo.eventoRelacionado}",
            render_to_string('email/alerta_admin_nuevoinscripto.html', datos),
            from_email, [from_email] + DESTINATARIOS_ADMIN)
        msg.content_subtype = 'html'
        msg.send()
    except Exception:
        ok = False
        logger.exception('No se pudo enviar el aviso de inscripcion %s a la asociacion', nuevo.pk)
    try:
        msg2 = EmailMessage(
            f"Gracias {persona} por inscribirte en {nuevo.eventoRelacionado}",
            render_to_string('email/bienvenida_inscripto.html', datos),
            from_email, [persona.email])
        msg2.content_subtype = 'html'
        msg2.send()
    except Exception:
        ok = False
        logger.exception('No se pudo enviar la confirmacion de inscripcion %s a %s', nuevo.pk, persona.email)
    return ok


# Create views EVENTOS - USUARIO------------------------------

def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


def listPruebas(request):
    eventos = Eventos.objects.all()

    return render(request, 'inscripcion/list_pruebas.html', {'eventos': eventos})



class InscripcionEventoList(ListView):
    model = Inscripcion
    template_name = 'inscripcion/lista_pagos_Eventos.html'

    def get_queryset(self):
        # Antes traia TODAS las inscripciones y filtraba en el template (miles de consultas).
        return (Inscripcion.objects.filter(persona=self.request.user)
                .select_related('persona', 'eventoRelacionado__tipo'))

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)


class InscripcionEventoListPublico(ListView):
    model = Inscripcion
    template_name = 'inscripcion/lista_inscriptos_publico.html'
    ordering = ['persona', ]

    def get_queryset(self):
        return (Inscripcion.objects.filter(eventoRelacionado=self.kwargs.get('pk'))
                .select_related('persona', 'eventoRelacionado__tipo').order_by('persona'))

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
        context['modalidad_evento']= ModalidadEventos.objects.filter(evento=filtro)
        asociados = Asociado.objects.filter(persona=self.request.user)
        lista = []
        for asociado in asociados:
            lista.append(asociado)
        context['asociado'] = lista
        evento = Eventos.objects.filter(id=filtro).first()
        edad = edad_al(self.request.user.fechaNacimiento, evento.fechaEvento if evento else None)
        context['es_menor'] = edad is not None and edad < 18
        # context['distancia'] = EventoDistancia.objects.all()
        # context['categoria'] = EventoCategoria.objects.all()
        return context


    def form_valid(self, form, **kwargs):
        form.instance.persona = self.request.user
        persona = form.instance.persona
        filtro = self.kwargs.get('pk', None)
        eventos = []
        for e in Eventos.objects.filter(id=filtro):
            eventos.append(e)
        form.instance.eventoRelacionado = eventos[0]

        edad = edad_al(persona.fechaNacimiento, eventos[0].fechaEvento)
        if edad is not None and edad < 18 and faltan_datos_menor(form):
            return self.form_invalid(form)

        nuevo = form.save(commit=False)
        nuevo.save()

        self.request.session['email_inscripcion_ok'] = enviar_emails_inscripcion(persona, nuevo)
        self.object = nuevo
        return redirect('inscripcion_recibida', pk=nuevo.pk)






class InscripcionPublicoEventoCreate(SuccessMessageMixin, CreateView):
    model = Persona
    template_name = 'inscripcion/form_inscripcion_publico.html'
    form_class = PersonaForm
    second_form = InscripcionForm
    success_url = reverse_lazy('eventos')
    success_message = "Gracias por inscribirte, ahora te redireccionamos a tu cuenta!"

    def get_context_data(self, **kwargs):
        context = super(InscripcionPublicoEventoCreate,self).get_context_data(**kwargs)
        filtro = self.kwargs.get('pk', None)
        context['eventos'] = Eventos.objects.filter(id=filtro)
        context['costos'] = EventoCosto.objects.filter(evento=filtro)
        context['modalidad_evento']= ModalidadEventos.objects.filter(evento=filtro)
        if 'form' not in context:
            context['form'] = self.form_class()
        if 'form2' not in context:
            context['form2'] = self.second_form()
        context['evento_id'] = filtro
        return context


    def post(self, request, *args, **kwargs ):
        self.object = self.get_object
        form = PersonaForm(request.POST, request.FILES)
        form2 = InscripcionForm(request.POST, request.FILES)

        filtro = self.kwargs.get('pk', None)
        evento = Eventos.objects.filter(id=filtro).first()
        validos = form.is_valid() and form2.is_valid()
        edad = edad_al(form.cleaned_data.get('fechaNacimiento') if hasattr(form, 'cleaned_data') else None,
                       evento.fechaEvento if evento else None)
        menor = edad is not None and edad < 18
        if validos and menor and faltan_datos_menor(form2):
            validos = False

        if validos:
            persona = form.save(commit=False)
            nuevo = form2.save(commit=False)
            raw_password = secrets.token_urlsafe(8)  # una clave distinta por atleta
            persona.password = make_password(raw_password)
            persona.username = uuid.uuid4().hex[:9]
            cuil = persona.cuil
            dni = cuil[2:-1]
            persona.dni = dni
            persona.save()
            nuevo.persona = persona
            if nuevo.montoAbonado == None:
                nuevo.montoAbonado = 0

            filtro = self.kwargs.get('pk', None)
            eventos = []
            for e in Eventos.objects.filter(id=filtro):
                eventos.append(e)
            nuevo.eventoRelacionado = eventos[0]

            nuevo.save()

            email_ok = enviar_emails_inscripcion(persona, nuevo, password=raw_password)

            user = authenticate(self.request, username=persona.username, password=raw_password)

            if user is not None:
                login(self.request,user)


            self.request.session['email_inscripcion_ok'] = email_ok
            return redirect('inscripcion_recibida', pk=nuevo.pk)

        else:
            filtro = self.kwargs.get('pk', None)

            eventos = Eventos.objects.filter(id=filtro)
            costos = EventoCosto.objects.filter(evento=filtro)
            modalidad_evento = ModalidadEventos.objects.filter(evento=filtro)
            # Si el CUIL ya tiene cuenta, se le ofrece ingresar y seguir desde su cuenta
            cuil_existente = any(e.code == 'unique' for e in form.errors.as_data().get('cuil', []))
            context =  {'form': form, 'form2':form2,'eventos':eventos,'costos':costos,'modalidad_evento':modalidad_evento,
                        'evento_id': filtro, 'cuil_existente': cuil_existente, 'menor_detectado': menor}
            return render(request, self.template_name, context)
            #print(form.errors)
            #return super(InscripcionPublicoEventoCreate, self).post(request, *args, **kwargs)

        return redirect(self.get_success_url())


class InscripcionEventoUsuarioList(ListView):
    model = Inscripcion
    template_name = 'inscripcion/lista_pagos_eventos.html'

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)

class EventosList(ListView):
    model = Eventos
    queryset = Eventos.objects.filter(estado=True).order_by("fechaEvento")
    template_name = 'inscripcion/eventos.html'

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)


class EventosPublicoList(ListView):
    model = Eventos
    queryset = Eventos.objects.filter(estado=True).order_by("fechaEvento")
    template_name = 'inscripcion/eventos_publico.html'



class EventosListDetalles(ListView):
    model = Eventos
    template_name = 'inscripcion/detalle_evento.html'


    def get_context_data(self, **kwargs):
        context = super(EventosListDetalles, self).get_context_data(**kwargs)
        parametro = self.kwargs.get('parametro', None)
        context['eventos'] = Eventos.objects.filter(id=parametro)

        modalidad = []
        for e in ModalidadEventos.objects.filter(evento=parametro):
            modalidad.append(e.modalidad)

        distancias = []
        for e in ModalidadEventos.objects.filter(evento=parametro):
            for d in e.distancia_disponible.all():
                if d not in distancias:
                    distancias.append(d)

        context['modalidad'] = modalidad
        context['distancias'] = distancias

        return context

    def form_valid(self, form):
        form.instance.persona = self.request.user
        return super().form_valid(form)




@login_required
def inscripcion_recibida(request, pk):
    """Pantalla clara de 'tu inscripcion quedo registrada' (no depende de carteles externos)."""
    inscripcion = get_object_or_404(
        Inscripcion.objects.select_related('eventoRelacionado__tipo', 'persona'),
        pk=pk, persona=request.user)
    email_ok = request.session.pop('email_inscripcion_ok', True)
    return render(request, 'inscripcion/inscripcion_recibida.html',
                  {'inscripcion': inscripcion, 'email_ok': email_ok})


def cuil_registrado(request):
    """Para el formulario sin cuenta: dice si un CUIL ya tiene cuenta, asi se le ofrece ingresar."""
    from django.http import JsonResponse
    digitos = ''.join(c for c in request.GET.get('cuil', '') if c.isdigit())
    existe = len(digitos) == 11 and Persona.objects.filter(cuil=digitos).exists()
    return JsonResponse({'existe': existe})
