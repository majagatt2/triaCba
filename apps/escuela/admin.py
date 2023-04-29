from django.contrib import admin
from apps.escuela.models import *
from django.utils.html import format_html


# Register your models here.

class EscuelaPagosAdmin(admin.ModelAdmin):
    list_display = ('asociado',  'tipoPago', 'fechaPago', 'formaPago',
                    'montoAbonado',  'comprobante', 'confirm_pago')
    list_filter = ('confirm_pago', 'asociado','formaPago')
    list_editable = ('confirm_pago',)
    date_hierarchy = "fechaPago"

    ordering = ('-fechaPago',)
    list_per_page = 10


    def comprobante(self, obj):
        return format_html('<a href={url}><img src={url} width="30" height="30" /></a>', url=obj.comprobPago.url)



class EscuelaCostoAdmin(admin.ModelAdmin):

    list_display = ('id', 'formaPago', 'precio')
    list_editable = ('precio',)
    #list_filter = ('formaPago')


class EscuelaTurnosAdmin(admin.ModelAdmin):

    list_display = ('id', 'nombre', 'cupo_turno','desde','hasta')
    list_editable = ('cupo_turno','desde','hasta')


class EscuelaEntrenadoresAdmin(admin.ModelAdmin):

    list_display = ('id', 'nombre', 'edad','mail', 'telefono')
    list_editable = ()


class EscuelaFuncionesProfesAdmin(admin.ModelAdmin):

    list_display = ('id', 'funcion', 'descripcion')
    list_editable = ()


class EscuelaAsignTurnoAdmin(admin.ModelAdmin):

    list_display = ('id', 'entrenador', 'turno','funcion' ,'hs_semanal','habilitado')
    list_editable = ('funcion','hs_semanal','habilitado')
    




admin.site.register(EscuelaFormasPago)
admin.site.register(EscuelaCosto, EscuelaCostoAdmin)
admin.site.register(EscuelaPagos, EscuelaPagosAdmin)
admin.site.register(EscuelaTurnos, EscuelaTurnosAdmin)
admin.site.register(EscuelaEntrenadores, EscuelaEntrenadoresAdmin)
admin.site.register(EscuelaAsignacTurno, EscuelaAsignTurnoAdmin)
admin.site.register(EscuelaFuncionesProfes,EscuelaFuncionesProfesAdmin)
