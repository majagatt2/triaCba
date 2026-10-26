#from ast import Pass
from django.db import models
from datetime import  date
#from django.utils import timezone
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
#from django.dispatch import receiver
#from django.db.models.signals import post_save
from apps.registro.validators import validate_field_size
from django.core.exceptions import ValidationError
from apps.inscripcion.validators import validar_cuil


# Create your models here.


class Persona(AbstractUser):

    cuil = models.CharField(max_length=11, help_text="sin guiones", primary_key=True,validators=[validar_cuil])
    dni = models.CharField(max_length=80)
    domicilio = models.CharField(max_length=80)
    ciudad = models.CharField(max_length=60)
    telefono = models.CharField(max_length=40)
    fechaNacimiento = models.DateField()  # default=date.today para cuando inicio primera vez
    nacionalidad = models.CharField(max_length=12, default='Argentina')
    sexo = models.CharField(max_length=10, choices=[('F', 'Mujer'), ('M', 'Hombre')],
                            null=False, verbose_name='Sexo')
    fotoPerfil = models.FileField(upload_to='media/fotoPerfil',null=True, blank=True,default='media/fotoPerfil/Default_1234.png',validators=[validate_field_size])#,default='foto Perfil'
    fotoDni = models.FileField(upload_to='media/fotoDni',null=False, blank=False, default='foto Dni',validators=[validate_field_size])#, default='foto Dni'


    class Meta:
        verbose_name= 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['last_name', 'first_name']

    def clean(self):
        if not validar_cuil(self.cuil):
             raise ValidationError({'cuil': "CUIL inválido"})
        super().clean()


    def __str__(self):
        return f"{self.last_name.title()} {self.first_name.title()}"

    @property
    def inst_fotoPerfil_file(self):
        if self.fotoPerfil :
            return self.fotoPerfil.url
        return ''

    @property
    def inst_fotoDni_file(self):
        if self.fotoDni :
            return self.fotoDni.url
        return ''


    @property
    def get_edad(self):
        today = date.today()
        edad = today.year - self.fechaNacimiento.year - \
            ((today.month, today.day) <
             (self.fechaNacimiento.month, self.fechaNacimiento.day))
        return edad


