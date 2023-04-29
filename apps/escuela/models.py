from django.db import models
from apps.socio.models import Asociado
from datetime import date

# Create your models here.


class EscuelaFormasPago(models.Model):
    formaPago = models.CharField(max_length=40)

    

    def __str__(self):
        return f"{self.formaPago}"


class EscuelaCosto(models.Model):
    
    formaPago = models.ForeignKey(EscuelaFormasPago, default=1, on_delete=models.CASCADE, null=True)
    precio = models.IntegerField()
    
    def __str__(self):
        return f"{self.formaPago} - ${self.precio}"
    

class EscuelaPagos(models.Model):
    asociado = models.ForeignKey(Asociado, null=True, blank=True,
                                        on_delete=models.CASCADE, verbose_name='Persona Asociada')
    opcionElegida = models.ForeignKey(
        EscuelaCosto, null=True, blank=True, on_delete=models.CASCADE, verbose_name="Opcion Elegida")

    tipoPago = models.CharField(
        max_length=40,  blank=True, null=True, verbose_name="Entrenador :")
    formaPago = models.CharField(
        max_length=40,  blank=True, null=True, verbose_name="Forma pago")
    montoDebeAbonar = models.IntegerField(
        null=True, blank=True, verbose_name="Monto a abonar:")
    montoAbonado = models.IntegerField(
        null=True, verbose_name="Monto Abonado:")
    comentario = models.CharField(
        ("Comentarios"), max_length=150, null=True, blank=True)
    fechaPago = models.DateField(verbose_name="Fecha pago")
    comprobPago = models.ImageField(
        upload_to='media/pagos', null=False, default="comprobante de Pago", verbose_name="Comprobante de pago")
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
    
    @property
    def get_anio(self):
        fecha = self.fechaPago
        anio = fecha.year
        return anio
        
    @property
    def get_mes(self):
        fecha = self.fechaPago
        anio = fecha.month
        return anio

    
        
    @property
    def get_montoAbonado(self):
        monto = 0
        monto += self.montoAbonado
        return monto
    
    
        

class EscuelaTurnos(models.Model):
    nombre = models.CharField(max_length=8)
    cupo_turno = models.IntegerField()
    desde = models.TimeField()
    hasta = models.TimeField()

    def __str__(self):
        return f"{self.nombre}"
        
class EscuelaEntrenadores(models.Model):
    nombre = models.CharField(max_length=40)
    dni = models.IntegerField(null=True, blank=True)
    nacionalidad = models.CharField(max_length=12, default='Argentina')
    mail = models.EmailField(null=True, blank=True)
    telefono = models.IntegerField(default=0, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    observacion = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"{self.nombre}"
    
    @property
    def edad(self):
        return date.today().year - self.fecha_nacimiento.year
    

class EscuelaFuncionesProfes(models.Model):
    funcion = models.CharField(max_length=20)
    descripcion = models.CharField(max_length=100, null=True, blank=True)
    

    def __str__(self):
        return f"{self.funcion}"
    
    
    
class EscuelaAsignacTurno(models.Model):
    entrenador = models.ForeignKey(EscuelaEntrenadores, verbose_name=("Entrenador"), on_delete=models.CASCADE)
    turno = models.ForeignKey(EscuelaTurnos, on_delete=models.CASCADE)
    funcion = models.ForeignKey(EscuelaFuncionesProfes, on_delete=models.CASCADE)
    habilitado = models.BooleanField(default=False)
    hs_semanal = models.IntegerField(("Hs semanales"), default=0)
    seguro_escuela = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.entrenador}"

    
class EscuelaAsistencia(models.Model):
    fecha = models.DateField(("Fecha"), auto_now=False, auto_now_add=True)
    asociado = models.ForeignKey(Asociado, verbose_name=("Asociado"), on_delete=models.CASCADE)
    asistencia = models.BooleanField(("Asistencia"))
    comentario = models.CharField(("Comentario"),default="",null=True, blank=True ,max_length=100)