from ast import Pass
from django.db import models
from datetime import datetime, date, timedelta
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.


class Persona(AbstractUser):
   
    cuil = models.CharField(max_length=11, help_text="sin guiones", primary_key=True)
    dni = models.IntegerField(default=0)
    domicilio = models.CharField(max_length=80)
    ciudad = models.CharField(max_length=60)
    telefono = models.CharField(max_length=40)
    fechaNacimiento = models.DateField()  # default=date.today para cuando inicio primera vez
    nacionalidad = models.CharField(max_length=12, default='Argentina')
    sexo = models.CharField(max_length=10, choices=[('F', 'Mujer'), ('M', 'Hombre')],
                            null=False, verbose_name='Sexo')
    fotoPerfil = models.ImageField(
        upload_to='media/fotoPerfil', null=False)  # default='foto Perfil'
    fotoDni = models.ImageField(
        upload_to='media/fotoDni')  # default='foto Dni'
    
    
    class Meta:
        verbose_name= 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ['last_name', 'first_name']
        
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"    
    
    
    @property
    def get_edad(self):
        return date.today().year - self.fechaNacimiento.year 
   