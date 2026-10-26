from django import forms
from apps.socio.models import *
from django.forms.fields import DateField, ImageField





class SocioForm(forms.ModelForm):
   #fecha = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}), )
    emmac_file = forms.FileField(widget=forms.FileInput(attrs={'class': 'form-control','accept': 'image/jpg,image/jpeg,image/png'}), label="Adjuntar foto de emmac. Sólo formato jpg o png hasta 2Mb", required=False)

    entrenador = forms.ModelChoiceField(widget=forms.Select(attrs={'class': 'form-control'}), required=True, queryset=EntrenadoresKempe.objects.filter(
        habilitado=True), label="Selecciona tu entrenador en Kempes*. Si no tienes, selecciona 'Sin Entrenador'", initial=12)

    fecha_emision_emmac = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False)

    #fechaPago = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date', 'class': 'form-control'}), label='Fecha de Pago del Comprobante*:')

    mail_responsable = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False, )

    numero_emmac = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Ingrese su número de emmac '}), max_length=8, required=False, label='Numero de Emmac*')

    obra_social = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Siglas de su obra social actual'}), max_length=60, required=True, label='Obra Social*', error_messages={'required':'Este dato es requerido','max_length': 'Hasta 60 caracteres'})




    class Meta:
        model = Asociado
        fields = ( 'con_entrenador','entrenador','fecha_emision_emmac', 'emmac_file','numero_emmac','obra_social', 'responsable_tutor','relacion_legal', 'dni_responsable', 'mail_responsable','telefono_responsable')

        labels = {
                #'fecha':'Fecha: se toma como referecia fecha pago contado o primera cuota',
                #'tipoAsociado': 'Tipo de Asociado*',
                'fecha_emision_emmac': 'Fecha emisión Emmac*',
                #'emmac_file': 'Adjuntar foto de emmac. Sólo formato jpg o png hasta 2Mb',
                'obra_social':'Obra Social*',
                'con_entrenador':'Tenes entrenador en el Kempes?:*',
                #'entrenador':"Selecciona tu entrenador en polo Kempes. Si no tienes, seleccion 'Sin Entrenador'",
                'responsable_tutor': 'Responsable Tutor',
                'relacion_legal: Relación legal con responsable tutor'
                'dni_responsable':' DNI responsable tutor',
                'mail_responsable':' email responsable tutor',
                'telefono_responsable':' Teléfono responsable tutor',
                  }

        widgets = {
            'tipoAsociado': forms.Select(attrs={'class': 'form-control'}),
            'con_entrenador': forms.Select(attrs={'class': 'form-control'}),
            'entrenador': forms.Select(attrs={'class': 'form-control'}),
            #'fecha_emision_emmac': forms.DateInput(attrs={'class': 'form-control'}),
            'numero_emmac': forms.TextInput(attrs={'class': 'form-control'}),
            'obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable_tutor': forms.TextInput(attrs={'class': 'form-control'}),
            'relacion_legal': forms.Select(attrs={'class': 'form-control'}),
            'dni_responsable': forms.NumberInput(attrs={'class': 'form-control'}),
            'telefono_responsable': forms.TextInput(attrs={'class': 'form-control'}),

        }



class PagosSocioForm(forms.ModelForm):

    fechaPago = DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}), label='Fecha de Pago del Comprobante*:')
    comentario = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Breve comentario si necesitas'}), max_length=150, required=False, label='Comentario')


    comprobPago = forms.FileField(widget=forms.FileInput(
        attrs={'accept': 'application/pdf,image/jpg,image/jpeg,image/png', 'class': 'form-control'}), label="Adjunte el comprobante de Pago* - Sólo jpg, jpeg, png y pdf hasta 2Mb*", required=True)

    class Meta:
        model = AsociadoPagos

        fields = ('opcionElegida', 'tipoAsociadoPago', 'formaPago', 'montoDebeAbonar',
                  'montoAbonado', 'comentario', 'fechaPago', 'comprobPago')

        labels = {
            'opcionElegida': 'Seleccione el tipo de Asociado y la forma de pago elegida*:',
            'tipoAsociadoPago': 'Tipo Asociado actual*:',
            'formaPago': 'Forma de Pago elegida*:',
            'montoDebeAbonar': 'Monto que corresponde abonar*:',
            'montoAbonado': 'Monto que Usted abonó*:',

        }

        widgets = {
            'opcionElegida': forms.Select(attrs={'class': 'form-control'}),

            'formaPago': forms.Select(attrs={'class': 'form-control'}),
            'montoDebeAbonar': forms.Select(attrs={'class': 'form-control'}),
            'montoAbonado': forms.NumberInput(attrs={'class': 'form-control'}),
            'fechaPago': forms.DateInput(attrs={'class': 'form-control'}),


        }



class EditSocioForm(forms.ModelForm):

    mail_responsable = forms.EmailField(
       widget=forms.EmailInput(attrs={'class': 'form-control'}), required=False, )


    class Meta:
        model = Asociado
        fields = ( 'emmac_file', 'numero_emmac','obra_social','con_entrenador',
                   'responsable_tutor', 'dni_responsable', 'telefono_responsable')

        labels = {
            #'fecha':'Fecha: se toma como referecia fecha pago contado o primera cuota',
            'emmac_file': 'Foto Emmac',
            'obra_social': 'Obra Social*',
            'con_entrenador': 'Tenes entrenador en el Kempes?:',
            'responsable_tutor': 'Responsable Tutor',
            'relacion_legal: Relación legal con responsable tutor'
            'dni_responsable': ' DNI responsable tutor',
            'mail_responsable': ' email responsable tutor',
            'telefono_responsable': ' Teléfono responsable tutor',
        }

        widgets = {

            'con_entrenador': forms.Select(attrs={'class': 'form-control'}),
            'numero_emmac': forms.TextInput(attrs={'class': 'form-control'}),
            'obra_social': forms.TextInput(attrs={'class': 'form-control'}),
            'responsable_tutor': forms.TextInput(attrs={'class': 'form-control'}),
            'relacion_legal': forms.Select(attrs={'class': 'form-control'}),
            'dni_responsable': forms.NumberInput(attrs={'class': 'form-control'}),
            'telefono_responsable': forms.TextInput(attrs={'class': 'form-control'}),


        }



