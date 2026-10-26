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
    list_display = ('fechaEvento', 'tipo', 'nombreEvento', 'lugar', 'cupo', 'estado','inscribirse','seguro','publicar','time_control')
    list_editable = ('cupo', 'estado','inscribirse','seguro','publicar','time_control')
    search_fields = ('año', 'fechaEvento', 'temporada',
                     'tipo', 'nombreEvento', 'lugar', 'estado')
    list_filter = ('año',  'temporada', 'tipo', 'lugar', 'estado')


class EventoCostoAdmin(admin.ModelAdmin):
    list_display = ('id', 'evento', 'asociado', 'formaPago', 'precio')
    list_editable = ('precio',)
    list_display_links = ('evento',)
    list_filter = ('evento',)


class EventoCategoriaAdmin(admin.ModelAdmin):
    list_display = ('id', 'categoria', 'sexo', 'edad_desde', 'edad_hasta')
    list_editable = ('edad_desde', 'edad_hasta')


class ModalidadEventosAdmin(admin.ModelAdmin):
    list_display = ('id',  'evento','modalidad',)
    list_editable = ('modalidad',)

class EventosDistanciaAdmin(admin.ModelAdmin):
    list_display = ('id',  'distancia')

class EventoFormasPagoAdmin(admin.ModelAdmin):
    list_display = ('id',  'formaPago')



class InscripcionAdmin(admin.ModelAdmin):
    list_display = ('persona','sexo', 'comprobante', 'control_pago', 'emmac_foto', 'foto_dni', 'confirm_pago','acreditacion','numero','numero_chip','modalidad','distancia', 'categoria', 'edad_31_Dic', 'forma_de_pago', 'montoAbonado','grupo', 'fechaPago',
                      'eventoRelacionado')

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
        forma = EventoCosto.objects.filter(id = id_forma)
        for f in forma:
            return f.formaPago


    # 'persona' como filtro cargaba las 1.600+ personas en la barra lateral: ahora se busca con el buscador
    list_filter = ('eventoRelacionado','distancia', 'categoria','grupo', 'confirm_pago','acreditacion', 'montoAbonado')
    search_fields = ('persona__last_name', 'persona__first_name', 'persona__cuil', 'persona__dni', 'persona__email')
    list_select_related = ('persona', 'eventoRelacionado__tipo')
    list_editable = ['categoria','control_pago','confirm_pago','acreditacion','numero','numero_chip',]
    list_per_page = 20


admin.site.register(Eventos, EventoAdmin)
admin.site.register(ModalidadEventos, ModalidadEventosAdmin)
admin.site.register(Inscripcion, InscripcionAdmin)
admin.site.register(EventoTipo)
admin.site.register(EventoDistancia)
admin.site.register(EventoModalidade)
admin.site.register(EventoCategoria, EventoCategoriaAdmin)
admin.site.register(EventoBici)
admin.site.register(EventoCosto, EventoCostoAdmin)
admin.site.register(EventoFormasPago, EventoFormasPagoAdmin)

