from django.contrib import admin
from apps.entrenadores.models import *
from django.utils.html import format_html


# Register your models here.

class EntrenadoresAdmin(admin.ModelAdmin):
    list_display = ('nombre',  'habilitado', 'seguro')
    list_filter = ()
    list_editable = ('habilitado', 'seguro')
    
    list_per_page = 10
    

class AsignardiasEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('entrenador',  'lugar','dias','turno')
    list_filter = ('turno','entrenador')
    list_editable = ('turno',)

    list_per_page = 10


admin.site.register(EntrenamientoTurno)
admin.site.register(DiasEntrenamiento)
admin.site.register(LugarEntrenamiento)
admin.site.register(Entrenadores,EntrenadoresAdmin)
admin.site.register(AsignarDiasEntrenamiento,AsignardiasEntrenamientoAdmin)
