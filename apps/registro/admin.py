from django.contrib import admin
#from import_export.Admin import ImportExportMixin
from apps.registro.models import *

# Register your models here.


class BienvenidaAdmin(admin.ModelAdmin):
    list_display = ('mensaje',)
    
    
admin.site.register(Bienvenida,BienvenidaAdmin)
