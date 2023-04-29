from django import forms
from apps.escuela.models import *
from django.forms.fields import DateField



class EscuelaPagosForm(forms.ModelForm):

    fechaPago = DateField(widget=forms.widgets.DateInput(
        attrs={'type': 'date', 'class': 'form-control'}), label='Fecha de Pago*:')
    comentario = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Breve comentario si necesitas'}), max_length=150, required=False, label='Comentario')
    comprobPago = forms.ImageField(required=True, widget=forms.FileInput(attrs={'class': 'form-control'}), label='Adjuntar Comprobante de Pago*: jpg o png')

   
    class Meta:
        model = EscuelaPagos

        fields = ('opcionElegida', 'tipoPago', 'formaPago', 'montoDebeAbonar',
                  'montoAbonado', 'comentario', 'fechaPago', 'comprobPago')

        labels = {
       
        'montoAbonado':'Monto Abonado*:',
        'montoDebeAbonar':'Monto que debe abonar*:',
        'formaPago':'Forma de pago elegida*:',
        'opcionElegida': 'Seleccione la cuota que abonó*:',
        'tipoPago':'Tipo Asociado*:',
        }

        widgets = {
            'opcionElegida': forms.Select(attrs={'class': 'form-control'}),
            'tipoPago': forms.Select(attrs={'class': 'form-control'}),
            'formaPago': forms.Select(attrs={'class': 'form-control'}),
            'montoDebeAbonar': forms.Select(attrs={'class': 'form-control'}),
            'montoAbonado': forms.NumberInput(attrs={'class': 'form-control'}),
            'fechaPago': forms.DateInput(attrs={'class': 'form-control'}),
            'comprobPago': forms.FileInput(attrs={'class': 'form-control'}),

        }


class AsistenciaForm(forms.ModelForm):
    asociado = forms.ModelChoiceField(
        queryset=Asociado.objects.filter(estado=True, tipoAsociado=5))
    
    comentario = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control', 'placeholder': 'Breve comentario si necesitas'}), max_length=150, required=False, label='Comentario')
    
    
    class Meta:
        model = EscuelaAsistencia
        
        fields = ('asociado', 'asistencia', 'comentario',)
        
        labels = {

           
        }

        widgets = {
            'asociado': forms.Select(attrs={'class': 'form-control'}),
           

        }


    