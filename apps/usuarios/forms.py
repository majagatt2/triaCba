from django.contrib.auth.models import User
from django.forms.fields import DateField, ImageField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.usuarios.models import Persona


class RegistroForm(UserCreationForm):
    fechaNacimiento = DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}), label="Fecha de Nacimiento")
    cuil = forms.CharField(widget=forms.TextInput(attrs={
                           'class': 'form-control', 'placeholder': 'Sin guiones'}), max_length=11)
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Nombres')
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Apellidos')

    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', }), required=True)

    fotoDni = ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control'}), label="Adjuntar foto de su DNI (Sólo jpg o png)")

    fotoPerfil = ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control'}), label="Adjuntar foto de Perfil (Sólo jpg o png)")
    
    
    class Meta:
        model = Persona
        fields = [
            
            'cuil',
            'dni',
            'first_name',
            'last_name',
            'username',
            'email',
            'domicilio', 'ciudad', 'telefono', 'fechaNacimiento', 'nacionalidad','sexo', 'fotoDni','fotoPerfil'
                  
        ]
        
        labels = {'fechaNacimiento':'Fecha de Nacimiento',}
        
        widgets = {
            #'cuil': forms.TextInput(attrs={'class': 'form-control'}),
            'dni': forms.NumberInput(attrs={'class': 'form-control'}),
            #'first_name': forms.TextInput(attrs={'class': 'form-control'}, required=True),
            #'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            #'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            
            

        }


class UpdatePersonaForm(forms.ModelForm):
    fechaNacimiento = DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date', }), label="Fecha de Nacimiento")
    fotoDni = DateField(
        widget=forms.FileInput(
            attrs={'class': 'form-control'}), label="Adjuntar foto de su DNI")

    fotoPerfil = DateField(
        widget=forms.FileInput(
            attrs={'class': 'form-control'}), label="Adjuntar foto de Perfil")

    class Meta:
        model = Persona
        
        exclude = ['password1', 'password2', ]
        
        fields = [

            'cuil',
            'first_name',
            'last_name',
            'username',
            'email',
            'domicilio', 'ciudad', 'telefono', 'fechaNacimiento', 'nacionalidad', 'sexo', 'fotoDni', 'fotoPerfil'

        ]

        labels = {'fechaNacimiento': 'Fecha de Nacimiento', }

        widgets = {



        }
