from dataclasses import fields
from django import forms
from apps.usuarios.models import Persona



        

class PersonForm(forms.ModelForm)    :
    class Meta:
        model = Persona
        fields = ['cuil', 'domicilio', 'ciudad', 'email', 'telefono', 'fechaNacimiento',  'sexo', 'fotoDni']
        


        

    