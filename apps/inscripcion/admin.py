from django.contrib import admin
from apps.inscripcion.models import *
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin
from PIL import Image

# Register your models here.

# class EventoAsignacionDistanciaAdmin(admin.TabularInline):
#     model = EventoAsignacionDistancia
#     extra = 1


# class EventoAsignacionModalidadAdmin(admin.TabularInline):
#     model = EventoAsignacionModalidad
#     extra = 1


# class EventoAsignacionCategoriaAdmin(admin.TabularInline):
#     model = EventoAsignacionCategoria
#     extra = 1

class EventoAdmin(admin.ModelAdmin):
    #inlines = [EventoAsignacionDistanciaAdmin, EventoAsignacionModalidadAdmin,EventoAsignacionCategoriaAdmin]
    list_display = ('fechaEvento', 'tipo', 'nombreEvento', 'lugar', 'cupo', 'estado','inscribirse','seguro','publicar')
    list_editable = ('cupo', 'estado','inscribirse','seguro','publicar')
    search_fields = ('año', 'fechaEvento', 'temporada',
                     'tipo', 'nombreEvento', 'lugar', 'estado')
    list_filter = ('año',  'temporada', 'tipo', 'lugar', 'estado')


class EventoCostoAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento', 'asociado', 'formaPago', 'precio')
    list_editable = ('precio',)
    list_display_links = ('evento',)


class EventoCategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'sexo', 'edad_desde', 'edad_hasta')
    list_editable = ('edad_desde', 'edad_hasta')


class ModalidadEventosAdmin(admin.ModelAdmin):
    list_display = ('id',  'evento','modalidad',)
    list_editable = ('modalidad',)
    

class ModalidadEventosAdmin(admin.ModelAdmin):
    list_display = ('id',  'evento', 'modalidad',)
    list_editable = ('modalidad',)
    

class EventosDistanciaAdmin(admin.ModelAdmin):
    list_display = ('id',  'distancia')
    
    
class EventosFormasPagoAdmin(admin.ModelAdmin):
    list_display = ('id',  'formaPago')




class InscripcionAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('persona','sexo', 'comprobante', 'emmac_foto', 'foto_dni', 'confirm_pago', 'acreditacion','numero','modalidad','categoria','distancia','edad_31_Dic', 'forma_de_pago', 'montoAbonado', 'grupo','fechaPago','eventoRelacionado')
    
    def comprobante(self, obj):
        if obj.comprobPago.url[-4:] == '.pdf':
            return format_html("<a href={url}> <p style='color:blue'><b>PDF</b></p></a>", url=obj.comprobPago.url)
        else:
            return format_html('<a href={url}><img src={url} width="40" height="40" /></a>', url=obj.comprobPago.url)
            
    


        
    def emmac_foto(self, obj):
        return format_html('<a href={url}><img src={url} width="40" height="40" /></a>', url=obj.emmac_file.url)
    
    def foto_dni(self, obj):
       
        return format_html('<a href={url}><img src={url} width="40" height="40" /></a>', url=obj.persona.fotoDni.url)
        
    

    def get_name(self, obj):
        nombre = obj.persona.last_name + " " + obj.persona.first_name
        return nombre.title()
    get_name.admin_order_field = 'nombre'
    get_name.short_description = 'Nombre'
    
    def sexo(self,obj):
        sexo = obj.persona.sexo
        return sexo
        
    
    def forma_de_pago(self, obj):
        id_forma = obj.formaPago
        forma = EventoFormasPago.objects.filter(id = id_forma)
        for f in forma:
            return f
    
    list_filter = ('eventoRelacionado', 'categoria',
                   'confirm_pago', 'persona', 'grupo','acreditacion')
    list_editable = ['categoria','confirm_pago','acreditacion','numero']
    list_per_page = 20
    
    
class ResultadosAdmin(ImportExportModelAdmin, admin.ModelAdmin):
    list_display = ('id','persona','evento','chip_corredor','tiempo_1','tiempo_2','tiempo_3','tiempo_finished')

    def persona(self, obj):
        persona = obj.inscripcion.persona
        return persona
    
    def evento(self, obj):
        evento = obj.inscripcion.eventoRelacionado
        return evento



admin.site.register(Eventos, EventoAdmin)
admin.site.register(ModalidadEventos, ModalidadEventosAdmin)
admin.site.register(Inscripcion, InscripcionAdmin)
admin.site.register(EventoTipo)
admin.site.register(EventoDistancia, EventosDistanciaAdmin)
admin.site.register(EventoModalidade)
admin.site.register(EventoCategoria, EventoCategoriaAdmin)
admin.site.register(EventoBici)
admin.site.register(EventoCosto, EventoCostoAdmin)
admin.site.register(EventoFormasPago, EventosFormasPagoAdmin)
admin.site.register(Resultados, ResultadosAdmin)

