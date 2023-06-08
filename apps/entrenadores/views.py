from django.shortcuts import render
from apps.entrenadores.models import AsignarDiasEntrenamiento
from django.views.generic import ListView, CreateView


# Create your views here.
class DiasAsignados(ListView):
    model = AsignarDiasEntrenamiento
    template_name = 'entrenadores/horarios.html'
