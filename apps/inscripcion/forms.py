from xml.dom.minidom import Attr
from django.db.models import F
from select import select
from tkinter.tix import Select
from django import forms
from apps.inscripcion.models import Inscripcion

from apps.inscripcion.models import  Eventos,EventoDistancia 
from django.forms.fields import DateField


class InscripcionForm(forms.ModelForm):

    fechaPago = DateField(widget=forms.widgets.DateInput(attrs={'type': 'date'}))
    
    
    class Meta:
        model = Inscripcion
        fields = [
            
            'eventoRelacionado',
            'distancia',
            'modalidad',
            'categoria',
            'bici',
            'obra_social',
            'emmac_file',
            'formaPago',
            'nombreEquipoPosta',
            'responsable_tutor',
            'dni_responsable',
            'relacion_legal',
            'mail_responsable',
            'telefono_responsable',
            'montoDebeAbonar',
            'montoAbonado',
            'fechaPago',
            'comprobPago',
            
            ]
        
        
        
        labels = {
                  'eventoRelacionado':'Evento que seleccionaste:',
                  'distancia':'Distancia:',
                  'modalidad':'Elija una Modalidad:',
                  'categoria':'Seleccione tu categoría:',
                  'bici':'Tipo de bici que usarás',
                  'nombreEquipoPosta':'En caso de Posta introduzca un nombre de Equipo',
                  'formaPago':'Forma de Pago:',
                  'montoDebeAbonar':'Monto que debe Abonar:',
                  'montoAbonado':'Monto Abonado:',
                  'fechaPago':'Fecha de Pago:',
                  'comprobPago':'Adjunte el comprobante de Pago',
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
