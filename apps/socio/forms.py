from django import forms
from apps.socio.models import *
from django.forms.fields import DateField





class SocioForm(forms.ModelForm):
    fecha = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    fecha_emision_emmac = DateField(
        widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    entrenador = forms.ModelChoiceField(queryset=EntrenadoresKempe.objects.filter(habilitado=True))
    

    class Meta:
        model = Asociado
        fields = ('fecha', 'tipoAsociado', 'fecha_emision_emmac', 'emmac_file','obra_social','con_entrenador', 'entrenador', 'responsable_tutor','relacion_legal', 'dni_responsable', 'mail_responsable','telefono_responsable')
        
        labels = {
                'fecha':'Fecha: se toma como referecia fecha pago contado o primera cuota',
                'tipoAsociado': 'Tipo de Asociado',
                'fecha_emision_emmac': 'Fecha emisión Emmac',
                'emmac_file':'Foto Emmac',
                'obra_social':'Obra Social',
                'con_entrenador':'Tenes entrenador en el Kempes?:',
                'entrenador':"Selecciona tu entrenador. Si no tenes, seleccion 'Sin Entrenador'",
                'responsable_tutor': 'Responsable Tutor. (Solo en caso de menores de 18 años)',
                'relacion_legal: Relación legal con responsable tutor'
                'dni_responsable':' DNI responsable tutor',
                'mail_responsable':' email responsable tutor',
                'telefono_responsable':' Teléfono responsable tutor',
                  }



class PagosSocioForm(forms.ModelForm):
   
    fechaPago = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    

    class Meta:
        model = AsociadoPagos
        
        fields = ('opcionElegida','tipoAsociadoPago','formaPago','montoDebeAbonar','montoAbonado','fechaPago','comprobPago')
        
        #labels = {}
        
        widgets = {
            'opcionElegida': forms.Select(attrs={'class': 'form-control'}),
            'tipoAsociadoPago': forms.Select(attrs={'class': 'form-control'}),
            'formaPago': forms.Select(attrs={'class': 'form-control'}),
            'montoDebeAbonar': forms.Select(attrs={'class': 'form-control'}),
            'montoAbonado': forms.NumberInput(attrs={'class': 'form-control'}),
            'fechaPago': forms.DateInput(attrs={'class': 'form-control'}),
            'comprobPago': forms.FileInput(attrs={'class': 'form-control'}),

        }

        
class EditSocioForm(forms.ModelForm):
  
    # fecha_emision_emmac = DateField(
    #     widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    

    class Meta:
        model = Asociado
        fields = ( 'emmac_file', 'obra_social','con_entrenador',
                   'responsable_tutor', 'dni_responsable', 'telefono_responsable')


