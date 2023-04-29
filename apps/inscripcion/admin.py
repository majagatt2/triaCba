from django.contrib import admin
from apps.inscripcion.models import *
from django.utils.html import format_html

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


class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('get_name', 'comprobante', 'emmac_foto', 'foto_dni', 'confirm_pago', 'categoria', 'get_edad', 'formaPago', 'montoAbonado', 'fechaPago',
                      'eventoRelacionado')
    
    def comprobante(self, obj):
        return format_html('<a href={url}><img src={url} width="40" height="40" /></a>', url=obj.comprobPago.url)
    
    def emmac_foto(self, obj):
        return format_html('<a href={url}><img src={url} width="40" height="40" /></a>', url=obj.emmac_file.url)
    
    def foto_dni(self, obj):
       
        return format_html('<a href={url}><img src={url} width="40" height="40" /></a>', url=obj.persona.fotoDni)
        

    def get_name(self, obj):
        nombre = obj.persona.last_name + " " + obj.persona.first_name
        return nombre
    get_name.admin_order_field = 'nombre'
    get_name.short_description = 'Nombre'
    
    list_filter = ('eventoRelacionado', 'categoria')
    list_editable = ['categoria','confirm_pago']
    list_per_page = 20
    

admin.site.register(Eventos, EventoAdmin)
#admin.site.register(EventoAsignaciones)
admin.site.register(Inscripcion, InscripcionAdmin)
admin.site.register(EventoTipo)
admin.site.register(EventoDistancia)
admin.site.register(EventoModalidade)
admin.site.register(EventoCategoria, EventoCategoriaAdmin)
admin.site.register(EventoBici)
admin.site.register(EventoCosto, EventoCostoAdmin)
admin.site.register(EventoFormasPago)

