

from unittest.util import _MAX_LENGTH
from django.db import models
from ckeditor.fields import RichTextField
from datetime import date
from django.core.validators import FileExtensionValidator
from apps.registro.validators import validate_field_size


from apps.socio.models import Asociado


from apps.usuarios.models import Persona
from apps.socio.models import Asociado

# Create your models here.


class EventoTipo(models.Model):
    tipoEvento = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.tipoEvento}"

    class Meta:
        verbose_name = "Tipo"
        verbose_name_plural = 'Tipos'


class EventoDistancia(models.Model):
    distancia = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.distancia}"

    class Meta:
        verbose_name = "Distancia"
        verbose_name_plural = 'Distancias'
        ordering = ['distancia']


class EventoModalidade(models.Model):
    modalidad = models.CharField(max_length=55)

    def __str__(self):
        return f"{self.modalidad}"

    class Meta:
        verbose_name = "Modalidad"
        verbose_name_plural = 'Modalidades'
        ordering = ['modalidad']


class EventoCategoria(models.Model):
    categoria = models.CharField(max_length=55)
    sexo = models.CharField(max_length=10, choices=[('F', 'Mujer'), ('M', 'Hombre')],
                            null=True, blank=True, verbose_name='Sexo')
    edad_desde = models.IntegerField(null=True, blank=True)
    edad_hasta = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.categoria}"

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = 'Categorias'
        ordering = ['categoria']


class EventoBici(models.Model):
    bici = models.CharField(max_length=30)

    def __str__(self):
        return f"{self.bici}"

    class Meta:
        verbose_name = "Bici"
        verbose_name_plural = 'Bicis'
        ordering = ['bici']


class Eventos(models.Model):
    año = models.IntegerField()
    fechaEvento = models.DateField(
        blank=False, null=False, help_text="Para competencias")
    fecha_calculo_edad = models.DateField(blank=False, null=False, default=date.today)
    temporada = models.CharField(max_length=25)
    tipo = models.ForeignKey(EventoTipo, verbose_name=(
        "Tipo"), on_delete=models.CASCADE)
     # modalidad_disponible = models.ManyToManyField(
    #     EventoModalidade)  # , through='EventoAsignacionModalidad'
    # categoria_disponible = models.ManyToManyField(
    #     EventoCategoria)  # , through='EventoAsignacionCategoria'
    # distancia_disponible = models.ManyToManyField(
    #     EventoDistancia)  # through='EventoAsignacionDistancia'
    # bici_disponible = models.ManyToManyField(
    #     EventoBici)  # through='EventoAsignacionDistancia'
    nombreEvento = models.CharField(max_length=60)
    lugar = models.CharField(max_length=25)
    cupo = models.IntegerField(blank=False, null=False)
    estado = models.BooleanField(("visible"), default=True)
    contenido = RichTextField()
    inscribirse = models.BooleanField(default=True)
    publicar = models.BooleanField(default=False)
    seguro = models.BooleanField(default=False)
    time_control = models.BooleanField(("Andres"),default=False)

    class Meta:
        verbose_name = 'EVENTO'
        verbose_name_plural = 'EVENTOS'
        ordering = ['-fechaEvento']

    def __str__(self):
        return f"{self.tipo} - {self.lugar} - {self.nombreEvento} - {self.fechaEvento.strftime('%d/%m/%Y')}  "



#     def __str__(self):
#         return f"{self.id} - {self.distancia} - {self.evento}"

# class EventoAsignacionModalidad(models.Model):
#     modalidad = models.ForeignKey(EventoModalidade, blank=True, null=True, on_delete=models.CASCADE)
#     evento = models.ForeignKey(Eventos, blank=True, null=True, on_delete=models.CASCADE)
#     nota = models.CharField(max_length=100, null=True, blank=True)


#     def __str__(self):
#         return f"{self.modalidad}"


# class EventoAsignacionCategoria(models.Model):
#     categoria = models.ForeignKey(EventoCategoria, blank=True, null=True, on_delete=models.CASCADE)
#     evento = models.ForeignKey(Eventos, blank=True, null=True, on_delete=models.CASCADE)
#     nota = models.CharField(max_length=100, null=True, blank=True)

#     def __str__(self):
#         return f"{self.categoria}"
class ModalidadEventos(models.Model):
    evento = models.ForeignKey(Eventos, verbose_name=(
        "Evento"), on_delete=models.CASCADE)
    modalidad = models.ForeignKey(
        EventoModalidade, null=True, blank=True, on_delete=models.CASCADE)
    categoria_disponible = models.ManyToManyField(
        EventoCategoria)
    distancia_disponible = models.ManyToManyField(
        EventoDistancia)  # through='EventoAsignacionDistancia'
    bici_disponible = models.ManyToManyField(
        EventoBici)  # through='EventoAsignacionDistancia'

    def __str__(self):
        return f"{self.modalidad}"

    class Meta:
        verbose_name = "Modalidad Evento"
        verbose_name_plural = 'Modalidad Eventos'


class EventoFormasPago(models.Model):
    formaPago = models.CharField(max_length=40)

    def __str__(self):
        return f"{self.formaPago}"

    class Meta:
        verbose_name = "Forma de Pago"
        verbose_name_plural = 'Formas de Pago'


class EventoCosto(models.Model):
    opciones = ()
    evento = models.ForeignKey(Eventos, verbose_name=(
        "Evento"), on_delete=models.CASCADE)
    asociado = models.CharField(
        max_length=20, choices=[('1', 'Asociado'), ('2', 'No Asociado')], default='', null=False)
    formaPago = models.ForeignKey(
        EventoFormasPago, verbose_name=("Forma"), on_delete=models.CASCADE)
    precio = models.IntegerField()

    def __str__(self):
        return f"{self.formaPago}"

    class Meta:
        verbose_name = "Costo"
        verbose_name_plural = 'Costos'


class Inscripcion(models.Model):
    persona = models.ForeignKey(Persona, null=False, blank=False, on_delete=models.CASCADE)
    eventoRelacionado = models.ForeignKey(Eventos, null=True, blank=True,
                                          on_delete=models.CASCADE,help_text='')
    distancia = models.CharField(max_length=60, null=False, blank=False, default='Elegir')
    modalidad = models.CharField(max_length=60, null=False, blank=False, default='Elegir')
    categoria = models.CharField(
        max_length=60, null=False, blank=False, default='Elegir')
    bici = models.CharField(max_length=40, null=False,
                            blank=False, default='Elegir')
    nombreEquipoPosta = models.CharField(
        max_length=40, help_text="", default='', null=True, blank=True)
    formaPago = models.CharField(max_length=40, null=False, blank=False)
    montoDebeAbonar = models.IntegerField()
    montoAbonado = models.IntegerField(default=0)
    fechaPago = models.DateField()
    # comprobPago = models.ImageField(
    #     upload_to='media/pagos', null=True, default="media/pagos/sin_costo.jpg", validators=[validate_file_size])

    comprobPago = models.FileField(
        (""), upload_to='media/pagos',
        default="media/pagos/sin_costo.jpg",
        validators=[validate_field_size]
        )


    comentario = models.CharField(("Comentarios"), max_length=150, null=True, blank=True)
    grupo = models.CharField(("Grupo"), max_length=30, null=True, blank=True)

    emmac_file = models.FileField(
        upload_to='media/eventos/emmac_certif', null=False, blank=False, default="emmac_file",verbose_name='Foto Emmac o Certifidado Medico - Sólo .jpg o .png *',validators=[validate_field_size])

    obra_social = models.CharField(max_length=60, null=False, blank=False)

    responsable_tutor = models.CharField(max_length=40, null=True, blank=True, help_text="Obligatorio en caso de ser menor de 18 años")
    relacion_legal = models.CharField(
        max_length=2, choices=[('1', '------'), ('2', 'Madre'), ('3', 'Padre'), ('4', 'Otro')], default='' ,null=True, blank=True)
    relacion = models.CharField(
        ("Defina Relación"), max_length=50, default='', null=True, blank=True)
    dni_responsable = models.IntegerField( null=True, blank=True)
    mail_responsable = models.EmailField(null=True, blank=True)
    telefono_responsable = models.CharField(max_length=20 , blank=True, null=True)

    control_pago = models.BooleanField(default=False, verbose_name='CP')
    confirm_pago = models.BooleanField(default=False, verbose_name='Aprobado')
    acreditacion = models.BooleanField(default=False, verbose_name='Acreditado')
    numero = models.IntegerField(("Nº corredor"), default=0, null=True, blank=True)
    numero_chip = models.IntegerField(
        ("Nº Chip"), default=0, null=True, blank=True)


    class Meta:
        ordering = ['-fechaPago']
        verbose_name = "Inscripcion"
        verbose_name_plural = 'Inscripciones'

    def get_dif_inscripcion(self):
        dif = self.montoAbonado - self.montoDebeAbonar
        return dif



    def montoAbonar(self):
        if self.eventoRelacionado.asociado == 'SI' and self.formaPago:
            self.montoDebeAbonar = self.eventorelacionado.precio
        else:
            if self.eventoRelacionado.asociado == 'NO' and self.formaPago:
                self.montoDebeAbonar = self.eventorelacionado.precio
        return self.montoDebeAbonar

    def siAsociado(self):
        estado = False
        asociado = Asociado.objects.all()
        for a in asociado:
            if a.persona == self.persona:
                if a.estado == True:
                    estado = True
                else:
                    estado = False
        return estado


    @property
    def get_edad(self):
        today = self.eventoRelacionado.fechaEvento
        edad = today.year - self.persona.fechaNacimiento.year - ((today.month, today.day) <
                                                         (self.persona.fechaNacimiento.month, self.persona.fechaNacimiento.day))
        return edad

    @property
    def edad_31_Dic(self):

        fecha_calculo_edad = self.eventoRelacionado.fecha_calculo_edad
        edad = fecha_calculo_edad.year - self.persona.fechaNacimiento.year - ((fecha_calculo_edad.month, fecha_calculo_edad.day) <
                                                                             (self.persona.fechaNacimiento.month, self.persona.fechaNacimiento.day))

        return edad




