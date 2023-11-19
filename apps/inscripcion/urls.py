from django.urls import path
from django import views
from django.conf import settings
from django.conf.urls.static import static
#from apps.inscripcion.views import *
from apps.inscripcion.views import EventosListDetalles, EventosList, EventosPublicoList, InscripcionEventoUsuarioList, InscripcionEventoCreate, InscripcionEventoList,InscripcionEventoListPublico, listPruebas, InscripcionPublicoEventoCreate, consulta_cuil, Resultados
from django.contrib.auth.decorators import login_required


urlpatterns = [
    
    path('pruebas/', listPruebas,name='pruebas'),
    
    path('eventos/', login_required(EventosList.as_view()), name='eventos'),
    
    path('eventos_publico/', EventosPublicoList.as_view(), name='eventos_publico'),
    
    
    
    path('inscribirme/<pk>', login_required(InscripcionEventoCreate.as_view()), name='inscribirme'),
    
    path('inscripcion_publico/<pk>', InscripcionPublicoEventoCreate.as_view(), name='inscripcion_publico'),
    
    path('lista_inscriptos/<pk>',InscripcionEventoListPublico.as_view(), name='lista_inscriptos'),
    
    path('mis_inscripciones/', login_required(InscripcionEventoList.as_view()), name='mis_inscripciones'),
    path('eventos_detalles/<parametro>', EventosListDetalles.as_view(), name='eventos_detalles'),
    
    path('consulta_cuil/<cuil>',consulta_cuil, name='consulta_cuil'),
    
    path('resultados/',Resultados.as_view(), name='resultados'),
    
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
