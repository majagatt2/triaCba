from django.urls import path
from django import views
from django.conf import settings
from django.conf.urls.static import static
#from apps.inscripcion.views import *
from apps.inscripcion.views import EventosListDetalles, EventosList, InscripcionEventoUsuarioList, InscripcionEventoCreate, InscripcionEventoList, listPruebas
from django.contrib.auth.decorators import login_required


urlpatterns = [
    
    path('pruebas/', listPruebas,name='pruebas'),
    
    path('eventos/', login_required(EventosList.as_view()), name='eventos'),
    path('inscribirme/<pk>', login_required(InscripcionEventoCreate.as_view()), name='inscribirme'),
    path('mis_inscripciones/', login_required(InscripcionEventoList.as_view()), name='mis_inscripciones'),
    path('eventos_detalles/<parametro>', login_required(EventosListDetalles.as_view()), name='eventos_detalles'),
    
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
