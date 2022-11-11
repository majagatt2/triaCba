from django.contrib.auth.models import User
from django.forms.fields import DateField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.usuarios.models import Persona


class RegistroForm(UserCreationForm):
    fechaNacimiento = DateField(widget = forms.widgets.DateInput(attrs={'type': 'date',}))
    
    
    class Meta:
        model = Persona
        fields = [
            
            'cuil',
            'first_name',
            'last_name',
            'username',
            'email',
            'domicilio', 'ciudad', 'telefono', 'fechaNacimiento', 'nacionalidad','sexo', 'fotoDni','fotoPerfil'
                  
        ]
        
        labels = {'fechaNacimiento':'Fecha de Nacimiento',}
        
        widgets = {
            
            

        }
