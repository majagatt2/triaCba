from django.contrib import admin
from apps.inscripcion.models import *
from django import forms
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
    list_display = ('fechaEvento', 'tipo', 'nombreEvento', 'lugar', 'cupo', 'estado','inscribirse','inscripcion_terminada','seguro','publicar','time_control')
    list_editable = ('cupo', 'estado','inscribirse','inscripcion_terminada','seguro','publicar','time_control')
    search_fields = ('año', 'fechaEvento', 'temporada',
                     'tipo', 'nombreEvento', 'lugar', 'estado')
    list_filter = ('año',  'temporada', 'tipo', 'lugar', 'estado')


class EventoCostoForm(forms.ModelForm):
    class Meta:
        model = EventoCosto
        fields = '__all__'

    def clean(self):
        datos = super().clean()
        evento, modalidades = datos.get('evento'), datos.get('modalidades')
        if evento and modalidades:
            ajenas = [m for m in modalidades if m.evento_id != evento.id]
            if ajenas:
                self.add_error('modalidades', 'Estas modalidades son de otro evento: '
                               + ', '.join(str(m.modalidad) for m in ajenas))
        return datos


class EventoCostoAdmin(admin.ModelAdmin):
    form = EventoCostoForm
    list_display = ('id', 'evento', 'asociado', 'formaPago', 'precio', 'para_modalidades')
    list_editable = ('precio',)
    list_display_links = ('evento',)
    list_filter = ('evento',)
    fields = ('evento', 'asociado', 'formaPago', 'precio', 'modalidades')

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('evento', 'formaPago').prefetch_related('modalidades__modalidad')

    @admin.display(description='Modalidades')
    def para_modalidades(self, obj):
        nombres = [str(m.modalidad) for m in obj.modalidades.all()]
        return ', '.join(nombres) if nombres else 'Todas'

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'modalidades':
            # Solo las modalidades del evento del costo (o, al crear uno nuevo, las de eventos proximos)
            object_id = request.resolver_match.kwargs.get('object_id') if request.resolver_match else None
            costo = EventoCosto.objects.filter(pk=object_id).first() if object_id else None
            qs = ModalidadEventos.objects.select_related('modalidad', 'evento')
            if costo:
                qs = qs.filter(evento=costo.evento)
            else:
                from datetime import timedelta
                from apps.inscripcion.models import hoy_cordoba
                qs = qs.filter(evento__fechaEvento__gte=hoy_cordoba() - timedelta(days=30))
            kwargs['queryset'] = qs.order_by('evento__fechaEvento', 'evento__nombreEvento', 'id')
            kwargs['widget'] = forms.CheckboxSelectMultiple
        field = super().formfield_for_manytomany(db_field, request, **kwargs)
        if db_field.name == 'modalidades':
            field.label_from_instance = lambda m: (
                f"{m.modalidad} — {m.evento.nombreEvento} ({m.evento.lugar}, {m.evento.fechaEvento:%d/%m/%Y})")
        return field


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

