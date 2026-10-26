from django.shortcuts import render
#from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
#from django.contrib.auth.forms import UserCreationForm
from apps.usuarios.models import Persona
from apps.usuarios.forms import RegistroForm, UpdatePersonaForm
from django.contrib.messages.views import SuccessMessageMixin  # for create and update
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
#from apps.registro.models import Bienvenida

from django.contrib.auth.views import  PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings



# Create your views para el USUARIO

def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


class PasswordResetViewTria(PasswordResetView):


    # def dispatch(self, request, *args, **kwargs):
    #     return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def form_valid(self, form):
        email = form.cleaned_data["email"]
        for user in form.get_users(email):
            if not user:
                continue

            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            context = {
                'email': user.email,
                'domain': self.request.get_host(),
                'site_name': 'triatloncordoba.org',
                'uid': uid,
                'user': user,
                'token': token,
                'protocol': 'https' if self.request.is_secure() else 'http',

            }

            reset_link = reverse('password_reset_confirm', kwargs={
                'uidb64': uid,
                'token': token,

            })

            context['reset_link'] = f"{context['protocol']}://{context['domain']}{reset_link}"

            subject = render_to_string(self.subject_template_name, context).strip()
            body = render_to_string(self.email_template_name, context)

            send_mail(subject, body, settings.EMAIL_HOST_USER, [user.email], fail_silently=False, html_message=body)


        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('password_reset_done')

class PasswordResetDoneViewTria(PasswordResetDoneView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('password_reset_confirm')

class PasswordResetConfirmViewTria(PasswordResetConfirmView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_success_url(self):
        return reverse('password_reset_complete')

class PasswordResetCompleteViewTria(PasswordResetCompleteView):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context



class UsuariosCreate(SuccessMessageMixin,CreateView):
    model = Persona
    template_name = "usuarios/form_crear_persona.html"
    form_class = RegistroForm
    success_url = reverse_lazy("login")
    success_message = "Gracias por Registrarte! Ya podes acceder desde la página principal"

    #ordering = ['nombre']
    def form_valid(self, form):
        cuil = form.instance.cuil
        dni = cuil[2:-1]
        form.instance.dni = dni
        return super().form_valid(form)



class DatosList(ListView):
    model = Persona
    template_name = 'usuarios/datos_personales.html'


class UsuariosUpdate(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Persona
    form_class = UpdatePersonaForm
    template_name = "usuarios/editar_persona.html"
    success_url = reverse_lazy('datos_usuarios')
    success_message = "Los datos se actualizaron con éxito"

    def form_valid(self, form, **kwargs):
        form.instance.password = self.request.user.password
        form.save()
        return super().form_valid(form)





# Create your views para ADMIN

class UsuariosList(ListView):
    model = Persona
    template_name = 'administrador/lista_personas.html'


class UsuariosEliminar(DeleteView):
    model = Persona
    template_name = 'administrador/eliminar_persona.html'
    success_url = reverse_lazy('lista_usuarios')

















