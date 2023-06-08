from django import forms
from apps.entrenadores.models import *
from django.forms.fields import DateField


class EntrenadoresForm(forms.ModelForm):
    class Meta:
        model = Entrenadores
