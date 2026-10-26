
from django import forms
from apps.inscripcion.models import Inscripcion
from apps.usuarios.models import Persona
from apps.inscripcion.models import  Eventos

from django.forms.fields import DateField, ImageField
from apps.inscripcion.validators import validar_cuil



class InscripcionForm(forms.ModelForm):

    fechaPago = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}),label='Fecha de pago:')
    comentario = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Breve comentario si necesitas'}), max_length=150, required=False, label='Comentario')
    grupo = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Obligatorio si pagas con descuento (Grupos, etc)', 'color':'blue'}), max_length=30, required=False, label='Código de descuento en pago:')
    obra_social = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Siglas de su obra social actual'}), max_length=60, required=True, label='Obra Social:*',error_messages={'required':'Este dato es requerido','max_length': 'Hasta 60 caracteres'})
    relacion = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Sólo si elegiste "Otro"'}), max_length=100, required=False, label='Relación:')
    responsable_tutor = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Nombres y Apellidos'}), max_length=100, required=False, label='Responsable Parental:')
    # comprobPago = ImageField(widget=forms.FileInput(attrs={
    #     'class': 'form-control'}), label="Adjunte el comprobante de Pago* - Sólo jpg o png hasta 2Mb*", required=True,)

    comprobPago = forms.FileField(widget=forms.FileInput(
        attrs={'accept': 'application/pdf,image/jpg,image/jpeg,image/png', 'class': 'form-control'}), label="Comprobante de pago* (foto jpg o png, o PDF de hasta 2 MB)", required=True)

    emmac_file = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control','accept': 'image/jpg,image/jpeg,image/png'}), label="Foto del Emmac o certificado médico* (jpg o png)", required=True,)


    class Meta:
        model = Inscripcion
        fields = [


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



        labels = {

                  'distancia':'Distancia:*',
                  'modalidad':'Modalidad elegida:*',
                  'categoria':'Seleccioná tu categoría:*',
                  'bici':'Tipo de bici que usarás*',
                  'nombreEquipoPosta':'En caso de Posta introduzca un nombre de Equipo. Mismo para cada integrante.',
                  'formaPago':'Seleccioná tu forma de pago:*',
                  'montoDebeAbonar':'Monto que debe Abonar:*',
                  'montoAbonado':'Monto que abonaste:*',
                  'fechaPago':'Fecha de Pago:*',
                  'comprobPago':'Adjunte el comprobante de Pago en caso de tener costo - Sólo jpg o png hasta 2Mb',
                  }



        widgets = {

            # 'formaPago': forms.Select(attrs={'class': 'form-control'}),
            'montoAbonado': forms.NumberInput(attrs={'class': 'form-control'}),
            'fechaPago': forms.DateInput(attrs={'class': 'form-control'}),
            'comprobPago': forms.FileInput(attrs={'class': 'form-control'}),
            'responsable_tutor':forms.TextInput(attrs={'class': 'form-control'}),
            'relacion_legal': forms.Select(attrs={'class': 'form-control'}),
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
                           'class': 'form-control','placeholder':'Sin guiones'}), validators=[validar_cuil],
                           error_messages={'unique': 'Ya tenés una cuenta con este CUIL. Tocá "Ingresar" arriba (o recuperá tu contraseña) y anotate desde Eventos.'})
    first_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Nombres')
    last_name = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'como figura en el DNI'}), max_length=100, required=True, label='Apellidos')

    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control',}), required=True)

    fotoDni = forms.FileField(widget=forms.FileInput(attrs={
        'class': 'form-control','accept': 'image/jpg,image/jpeg,image/png',}), label="Foto de tu DNI* (jpg o png)", required=True)

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


        labels = {
            'fechaNacimiento': 'Fecha de Nacimiento',
            'fotoDni':'Adjuntar foto de su DNI*. Sólo jpg o png hasta 2Mb',
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


        }


