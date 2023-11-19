from xml.dom.minidom import Attr
from django.db.models import F
from select import select
from tkinter.tix import Select
from django import forms
from apps.inscripcion.models import Inscripcion, EventoCategoria
from apps.usuarios.models import Persona 
from datetime import date
from apps.inscripcion.models import  Eventos,EventoDistancia 
from django.forms.fields import DateField, ImageField
from django.contrib.auth.forms import UserCreationForm
from betterforms.multiform import MultiModelForm, MultiForm
from collections import OrderedDict
from django.contrib.auth.hashers import make_password
import uuid



class InscripcionForm(forms.ModelForm):

    #fechaPago = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control','value':date.today}),label='Fecha de pago:')
    fechaPago = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}),label='Fecha de pago:')
    formaPago = forms.CharField(widget=forms.Select(attrs={
        'class': 'form-control', 'placeholder': 'Seleccione su forma de pago',}), max_length=100, required=True, label='Seleccion su forma de Pago*')
    comentario = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Breve comentario si necesitas', 'color':'blue'}), max_length=150, required=False, label='Comentario')
    grupo = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Sólo si perteneces a un grupo de pago', 'color':'blue'}), max_length=30, required=False, label='Código de Grupo de pago:')
    
    obra_social = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Siglas de su obra social actual'}), max_length=100, required=True, label='Obra Social*')
    relacion = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Sólo si elegiste "Otro"'}), max_length=100, required=False, label='Relación:')
    responsable_tutor = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nombres y Apellidos'}), max_length=100, required=False, label='REsponsable Parental:')
    # comprobPago = ImageField(widget=forms.FileInput(attrs={
    #     'class': 'form-control'}), label="Adjunte el comprobante de Pago* - Sólo jpg o png hasta 2Mb*", required=True,)
    comprobPago = forms.FileField(widget=forms.FileInput(
        attrs={'accept': 'application/pdf,image/jpg,image/jpeg,image/png', 'class': 'form-control'}), label="Adjunte el comprobante de Pago* - Sólo jpg, jpeg, png y pdf hasta 2Mb*", required=True)
    
    emmac_file = ImageField(widget=forms.FileInput(attrs={
        'class': 'form-control'}), label="Foto Emmac o Certifidado Medico* - Sólo jpg o png hasta 2Mb*", required=True,)
   
    
        
        
    
    class Meta:
        model = Inscripcion
       
        
        fields = [
            
            # 'eventoRelacionado',
            'distancia',
            'modalidad',
            'categoria',
            'bici',
            'obra_social',
            'emmac_file',
            'formaPago',
            'grupo',
            'nombreEquipoPosta',
            'responsable_tutor',
            'dni_responsable',
            'relacion_legal',
            'relacion',
            'mail_responsable',
            'telefono_responsable',
            'montoDebeAbonar',
            'montoAbonado',
            'comentario',
            'fechaPago',
            'comprobPago',
            
            ]
        
        def __init__(self, *args, **kwargs):
            super(InscripcionForm, self).__init__(*args, **kwargs)
            self.fields['categoria'].queryset = EventoCategoria.objects.none
                
        labels = {
                #   'eventoRelacionado':'Seleccioná tu competencia:',
                  'distancia':'Selecciona una distancia:',
                  'modalidad':'Modalidad elegida:',
                  'categoria':'Selecciona tu categoría:',
                  'bici':'Tipo de bici que usarás',
                  'nombreEquipoPosta':'En caso de Posta introduzca un nombre de Equipo',
                  'formaPago':'Seleccioná tu forma de Pago:',
                  'montoDebeAbonar':'Monto que debe Abonar:',
                  'montoAbonado':'Monto que abonaste:',
                  'fechaPago':'Fecha de Pago:',
                  'comprobPago':'Adjunte el comprobante de Pago',
                  }
        
    
    
        widgets = {
            
            # 'formaPago': forms.Select(attrs={'class': 'form-control'}),
            'montoAbonado': forms.NumberInput(attrs={'class': 'form-control'}),
            'fechaPago': forms.DateInput(attrs={'class': 'form-control'}),
            'comprobPago': forms.FileInput(attrs={'class': 'form-control'}),
            #'responsable_tutor':forms.TextInput(attrs={'class': 'form-control'}),
            'relacion_legal': forms.Select(attrs={'class': 'form-control','initial':'---'}, ),
            'dni_responsable':forms.NumberInput(attrs={'class': 'form-control'}),
            'mail_responsable': forms.EmailInput(attrs={'class': 'form-control'}),
            'telefono_responsable': forms.NumberInput(attrs={'class': 'form-control'}), 
            'obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'emmac_file': forms.FileInput(attrs={'class': 'form-control'}),
         }


class EventosForm(forms.ModelForm):
    class Meta:
        model = Eventos
        fields = '__all__'


class PersonaForm(forms.ModelForm):
    fechaNacimiento = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', 'class':'form-control'}), label="Fecha de Nacimiento")
    cuil = forms.CharField(widget=forms.TextInput(attrs={
                           'class': 'form-control','placeholder':'Sin guiones'}), max_length=11)
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Nombres')
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Apellidos')
    
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control',}), required=True)
    
    fotoDni = ImageField(
        widget=forms.FileInput(
            attrs={'class': 'form-control'}), label="Adjuntar foto de su DNI", required=True)

    # fotoPerfil = ImageField(
    #     widget=forms.FileInput(
    #         attrs={'class': 'form-control'}), label="Adjuntar foto de Perfil", required=False)

    class Meta:
        model = Persona
        #exclude = ['password1', 'password2', ]
        
        
        fields = [

            'cuil',
            #'dni',
            'first_name',
            'last_name',
            'email',
            'domicilio', 'ciudad', 'telefono', 'fechaNacimiento', 'nacionalidad', 'sexo', 'fotoDni'

        ]
        
        
        labels = {'fechaNacimiento': 'Fecha de Nacimiento', }

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
            

        }


# class UserCreationMultiForm(MultiModelForm):
#     form_classes = {
#         'form': PersonaForm,
#         'form2': InscripcionForm,
#     }

#     def save(self, commit=True):
#         objects = super(UserCreationMultiForm, self).save(commit=False)

#         if commit:
#             form = objects['form']
#             form.password = make_password('sin password')
#             form.username = uuid.uuid4().hex[:9]
#             form.save()
#             form2 = objects['form2']
#             form2.persona = form
#             form2.save()

#         return objects
