from logging import PlaceHolder
from django.db import models
from django.utils import timezone
from datetime import datetime, date, timedelta
from ckeditor.fields import RichTextField
#from apps.registro.models import AsociadoCosto, AsociadoFormasPago, AsociadoTipo , EntrenadoresKempe
from apps.usuarios.models import Persona


# Create your models here.
class AsociadoTipo(models.Model):
    tipoAsociado = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.tipoAsociado}"


class AsociadoFormasPago(models.Model):
    formaPago = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.formaPago}"


class AsociadoCosto(models.Model):
    tipoSocio = models.ForeignKey(AsociadoTipo, default=1,on_delete=models.CASCADE, null=True)
    formaPago = models.ForeignKey(
        AsociadoFormasPago, default=1, on_delete=models.CASCADE, null=True)
    precio = models.IntegerField()

    def __str__(self):
        return f"{self.tipoSocio} - {self.formaPago} - $ {self.precio}"
    # def get_tipoSocios(self):
    #     return ",".join([str(p) for p in self.tipoSocio.all()])

    # def get_formaPago(self):
    #     return ",".join([str(p) for p in self.formaPago.all()])


class EntrenamientoTurno(models.Model):
    nombre = models.CharField(max_length=8)
    cupo_turno = models.IntegerField()
    desde = models.TimeField()
    hasta = models.TimeField()

    def __str__(self):
        return f"{self.nombre}"


class EntrenadoresKempe(models.Model):
    nombre = models.CharField(max_length=25)
    cupo_entrenador = models.IntegerField(null=True, blank=True)
    turno = models.ForeignKey(EntrenamientoTurno, on_delete=models.CASCADE)
    mail = models.EmailField(null=True, blank=True)
    telefono = models.IntegerField(default=0, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    dni = models.IntegerField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=12, default='Argentina')
    observacion = models.CharField(max_length=50, null=True, blank=True)
    habilitado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombre}"
    
class AsociadoRequisitos(models.Model)    :
    requisitos = RichTextField()
    
    def __str__(self):
        return f"{self.requisitos}"
    


class Asociado(models.Model):
    persona = models.ForeignKey(Persona, null=True, blank=True, on_delete=models.CASCADE)
    fecha = models.DateField(default=date.today, null=False, blank=False)
    tipoAsociado = models.ForeignKey(
        AsociadoTipo, null=False, blank=False, on_delete=models.CASCADE)
    fecha_emision_emmac = models.DateField(
        default=date.today, null=False, blank=False)
    emmac_file = models.ImageField(
        upload_to='media/emmac', null=True, blank=True)
    obra_social = models.CharField(max_length=60, null=False, blank=False)
    con_entrenador = models.CharField(
        max_length=2, choices=[('1', 'SI'), ('2', 'NO')], default=2)
    entrenador = models.ForeignKey(EntrenadoresKempe, on_delete=models.CASCADE, null=False,blank=False, default=12, verbose_name='Entrenador Kempes')
    responsable_tutor = models.CharField(max_length=40, null=True, blank=True,default='', help_text="campos obligatorios en caso de ser menor de 18 años")
    relacion_legal = models.CharField(
        max_length=2, choices=[('1', '---------'), ('2', 'Madre'), ('3', 'Padre'), ('4', 'Tutor Legal')], default='', help_text="campo obligatorios en caso de ser menor de 18 años")
    dni_responsable = models.IntegerField(
        null=True, blank=True, help_text="campo obligatorios en caso de ser menor de 18 años")
    mail_responsable = models.EmailField(
        null=True, blank=True, help_text="campo obligatorios en caso de ser menor de 18 años")
    telefono_responsable = models.CharField(
        max_length=30,
        blank=True, null=True, help_text="campo obligatorios en caso de ser menor de 18 años")
    estado = models.BooleanField(default=False)
    vigente = models.BooleanField(default=True)
    
    
    
    def __str__(self):
        return f"{self.persona}"


    @property
    def get_vencimiento_emmac(self):
        vencimiento = self.fecha_emision_emmac + timedelta(days=365)
        return vencimiento

    @property
    def get_sit_emmac(self):
        if date.today() > self.get_vencimiento_emmac:
            return False
        else:
            return True
    
    @property
    def get_vencimiento(self):
        vencimiento = self.fecha + timedelta(days=365)
        return vencimiento
    
    
    @property
    def get_vigente(self):
        if self.get_vencimiento < date.today():
            return False
        else:
            return True
    
    @property
    def vigentes(self):
        cantidad = 0
        if self.get_vigente:
            cantidad += 1
        return cantidad
    
    
    @property
    def dias_vencer(self):
        if self.get_vencimiento > date.today():
            self.estado=True
        else:
            self.estado=False
        return self.estado
    
    

    @property
    def get_estado(self):
        if self.dias_vencer and self.estado and self.get_sit_emmac:
            self.estado = True
        else:
           self.estado = False
        return self.estado
     
        
    @property
    def fecha_actual(self):
        fecha_hora = datetime.now()
        return fecha_hora 
    
   
    
    
        
        
    
class AsociadoPagos(models.Model):
    personaAsociada = models.ForeignKey(Persona, null=True, blank=True,
                                 on_delete=models.CASCADE, verbose_name='PersonaAsociada')
    opcionElegida = models.ForeignKey(
        AsociadoCosto, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Referencia para elegir opciones de pago:")
    
    tipoAsociadoPago = models.CharField(
        max_length=40,  blank=True, null=True, verbose_name="Tipo Ascociado elegido:")
    formaPago = models.CharField(
        max_length=40,  blank=True, null=True, verbose_name="Forma de pago elegida:")
    montoDebeAbonar = models.IntegerField(
        null=True, blank=True, verbose_name="Monto que corresponde abonar:")
    montoAbonado = models.IntegerField(null=True)
    fechaPago = models.DateField(verbose_name="Fecha de pago del comprobante")
    comprobPago = models.ImageField(
        upload_to='media/pagos', null=True, default="comprobante de Pago", verbose_name="Adjuntar compropante de pago")
    confirm_pago = models.BooleanField(default=False)
    

    class Meta:
        ordering = ['fechaPago']
    
    
    def estado_pagos(self):
        if self.confirm_pago == False:
            return 'Revisar'
        else:
            return 'ok'    
      
   
    def get_diferencia(self):
        dif = self.montoDebeAbonar - self.montoAbonado
        return dif
       
    def siAsociado(self):
        estado = False
        asociado = Asociado.objects.all()
        for a in asociado:
            if a.persona == self.personaAsociada:
                if a.estado == True:
                    estado = True
                else:
                    estado = False
        return estado
   
    
   
   
    