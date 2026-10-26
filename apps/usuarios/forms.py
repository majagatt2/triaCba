from django.contrib.auth.models import User
from django.forms.fields import DateField, ImageField
from django import forms
from django.contrib.auth.forms import UserCreationForm
from apps.usuarios.models import Persona
from apps.inscripcion.validators import validar_cuil


class RegistroForm(UserCreationForm):
    fechaNacimiento = DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}), label="Fecha de Nacimiento")
    cuil = forms.CharField(widget=forms.TextInput(attrs={
                           'class': 'form-control', 'placeholder': 'Sin guiones'}), validators=[validar_cuil])
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Nombres')
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Apellidos')

    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control', }), required=True)

    fotoPerfil = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control','accept': 'image/jpg,image/jpeg,image/png',}), label="Adjuntar foto de Perfil (Sólo jpg o png hasta 2Mb)", required=False)

    fotoDni = forms.FileField(
        widget=forms.FileInput(
            attrs={'class': 'form-control','accept': 'image/jpg,image/jpeg,image/png',}), label="Foto Dni (Sólo jpg o png hasta 2Mb)", required=True)




    class Meta:
        model = Persona
        fields = [

            'cuil',
            #'dni',
            'first_name',
            'last_name',
            'username',
            'email',
            'domicilio', 'ciudad', 'telefono', 'fechaNacimiento', 'nacionalidad','sexo', 'fotoDni','fotoPerfil'

        ]

        labels = {
            'fechaNacimiento':'Fecha de Nacimiento',
            'fotoDni': 'Adjuntar foto de su DNI (Sólo jpg o png)',
        }

        widgets = {
            #'cuil': forms.TextInput(attrs={'class': 'form-control'}),
            #'dni': forms.NumberInput(attrs={'class': 'form-control'}),
            #'first_name': forms.TextInput(attrs={'class': 'form-control'}, required=True),
            #'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            #'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'domicilio': forms.TextInput(attrs={'class': 'form-control'}),
            'ciudad': forms.TextInput(attrs={'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'nacionalidad': forms.TextInput(attrs={'class': 'form-control'}),
            'sexo': forms.Select(attrs={'class': 'form-control'}),
            'fotoDni': forms.FileInput(attrs={'class': 'form-control'}),
            'fotoPerfil': forms.FileInput(attrs={'class': 'form-control'}),



        }

    def clean_cuil_field(self):
            cuil = self.cleaned_data.get('cuil')
            if not validar_cuil(cuil):
                raise forms.ValidationError("CUIL inválido.")
            return cuil

class UpdatePersonaForm(forms.ModelForm):
    fechaNacimiento = DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date', }), label="Fecha de Nacimiento")

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
