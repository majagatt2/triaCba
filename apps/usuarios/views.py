from django.shortcuts import render
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, Http404
#from django.contrib.auth.forms import UserCreationForm
from apps.usuarios.models import Persona
from apps.usuarios.forms import RegistroForm, UpdatePersonaForm
from django.contrib.messages.views import SuccessMessageMixin  # for create and update
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404


# Create your views para el USUARIO

def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


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
        
        
# class PersonasList(ListView):

#     model = Persona
#     template_name = 'registro/administrador/lista_personas.html'
#     paginate_by = 400

#     ordering = ['last_name']

         
  
    


    
    





 
    
    
