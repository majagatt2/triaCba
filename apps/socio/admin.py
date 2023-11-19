from django.contrib import admin
# from import_export.Admin import ImportExportMixin
from apps.socio.models import *
from django.utils.html import format_html
# Register your models here.


class AsociadoAdmin(admin.ModelAdmin):
    list_display = ('id','persona', 'fecha', 'tipoAsociado', 'entrenador', 'estado', 'asiste','fecha_emision_emmac', 'emmac_foto', 'get_vencimiento')
    list_editable = ['entrenador', 'fecha_emision_emmac', 'estado','asiste']
    list_filter = ('tipoAsociado',  'con_entrenador',  'entrenador', 'estado','persona',)
    list_display_links = ('persona',)
    #search_fields = ('persona',)
    
    list_per_page= 10
    
    def emmac_foto(self, obj):
        return format_html('<a href={url}><img src={url} width="40" height="40" /></a>', url=obj.emmac_file.url)
    
    
class AsociadoExportarAdmin(admin.ModelAdmin):
    list_display = ['get_name', 'fecha',
                    'tipoAsociado',  'con_entrenador', 'estado']


class AsociadoPagosAdmin(admin.ModelAdmin):
    list_display = ('personaAsociada','tipoAsociadoPago','fechaPago','montoAbonado','formaPago','comprobante','confirm_pago' )
    list_filter = ('confirm_pago','personaAsociada',)
    list_editable = ('confirm_pago',)
    
    ordering = ('-fechaPago',)
    list_per_page = 10
    
    def comprobante(self, obj):
        return format_html('<a href={url}><img src={url} width="30" height="30" /></a>', url=obj.comprobPago.url)


    # def get_name(self, obj):
    #     nombre = obj.asociado.last_name + " " + obj.asociado.first_name
    #     return nombre
    # get_name.admin_order_field = 'nombre'
    # get_name.short_description = 'Nombre'  # Renames column head


class EntrenamientoTurnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cupo_turno', 'desde', 'hasta')
    list_editable = ('cupo_turno', 'desde', 'hasta')


class EntrenadorAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'cupo_entrenador', 'turno', 'habilitado','seguro' )
    list_editable = ('cupo_entrenador', 'habilitado','seguro')
    

class DiasEntrenamientoAdmin(admin.ModelAdmin):
    list_display = ('dias',)
    
class AsignarDiasEntrenamientoAdmin(admin.ModelAdmin)    :
    list_display = ('entrenador', 'desde', 'hasta')
    

class AsociadoCostoAdmin(admin.ModelAdmin):
   
    list_display = ( 'id','tipoSocio','formaPago','precio')
    list_editable = ('precio',)
    list_filter = ('tipoSocio','formaPago')
   
class AsociadoRequisitosAdmin(admin.ModelAdmin):
    list_display = ('id',)

    
    
    

admin.site.register(Asociado, AsociadoAdmin)
admin.site.register(AsociadoTipo)
admin.site.register(AsociadoPagos, AsociadoPagosAdmin)
admin.site.register(AsociadoFormasPago)
admin.site.register(AsociadoCosto, AsociadoCostoAdmin)
admin.site.register(EntrenamientoTurno, EntrenamientoTurnoAdmin)
admin.site.register(EntrenadoresKempe, EntrenadorAdmin)
admin.site.register(AsociadoRequisitos, AsociadoRequisitosAdmin)
admin.site.register(DiasEntrenamiento, DiasEntrenamientoAdmin)
admin.site.register(AsignarDiasEntrenamiento, AsignarDiasEntrenamientoAdmin)
