#from importlib import resources
from django.contrib import admin
from apps.usuarios.models import Persona
from import_export import resources
from import_export.admin import ImportExportModelAdmin


# Register your models here.

class PersonaResource(resources.ModelResource):
    class meta:
        model = Persona
        fields = ('cuil','first_name','last_name',)
        #fields = ('author__name',) si siguiera la relacion hacia arriba
        #exclude = ()
        export_order = ('first_name', 'last_name', 'cuil',)


class PersonaAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('cuil', 'is_staff', 'first_name', 'last_name',
                    'username', 'email', 'sexo', 'get_edad')
    
    search_fields = ('cuil', 'first_name', 'last_name', 'username', 'email', 'domicilio',
                     'ciudad',  'telefono', 'fechaNacimiento', 'sexo')
    
    list_display_links = ('cuil','username',)
    
    resource_classes= [PersonaResource]
    
    list_filter = ('sexo','is_staff')
    
    #date_hierarchy = 'fechaNacimiento' #si quiero que el filtro aparezca arriba. Debe ser tipo DateField
    
    
    
    
admin.site.register(Persona,PersonaAdmin)