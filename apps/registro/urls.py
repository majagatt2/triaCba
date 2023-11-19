
from . import views
from django.urls import path
from apps.registro.views import *
from apps.registro.views import PersonasList, SociosList, AsociadoPagosList, AsociadoPagosEscuelaList, AsociadoPagosEscuelaList_mensual, AsociadosEscuelaList, AsociadosPublicoList, EventosList, InscriptosList, InscriptosPublicoList, EntrenadoresList, ResumenViews, ResumenViewsEscuela, SeguroListAsociados, SeguroListEntrenadores, SeguroListInscriptos, KempesList, AgenciaList
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


urlpatterns = [

    #path('', login_required(login), name='index'),
    
    path('index', login_required(bienvenida), name='index'),
    
    path('adminWeb', login_required(adminWeb), name='adminWeb'),
    
    path('lista_personas/', login_required(PersonasList.as_view()), name = 'lista_personas'),
    
    path('lista_asociado', SociosList.as_view(), name='lista_asociados'),
    
    path('lista_pagos_socios/', login_required(AsociadoPagosList.as_view()),name='lista_pagos_socios'),
    
    path('lista_pagos_escuelaAdmin/', login_required(AsociadoPagosEscuelaList.as_view()),name='lista_pagos_escuelaAdmin'),
    
    path('lista_pagos_escuelaAdmin_mensual/', login_required(AsociadoPagosEscuelaList_mensual.as_view()),
         name='lista_pagos_escuelaAdmin_mensual'),
    
    path('lista_escuela/', login_required(AsociadosEscuelaList.as_view()), name='lista_escuela'),
    
    path('lista_eventos/', login_required(EventosList.as_view()), name='lista_eventos'),
    
    path('lista_inscriptos_admin/<pk>', login_required(InscriptosList.as_view()), name='lista_inscriptos_admin'),
    
    path('lista_inscriptos_publico/', InscriptosPublicoList.as_view(),
          name='lista_inscriptos_publico'),
    
    path('lista_asociados_publico/', AsociadosPublicoList.as_view(),
         name='lista_asociados_publico'),
    
    path('lista_entrenadores/', login_required(EntrenadoresList.as_view()), name='lista_entrenadores'),
    
    path('resumen/', login_required(ResumenViews.as_view()), name='resumen'),
    
    path('estad_escuela/', login_required(ResumenViewsEscuela.as_view()), name='estad_escuela'),
    
    
    path('seguro_asociados/', SeguroListAsociados.as_view(), name='seguro_asociados'),
    
    path('seguro_entrenadores/', SeguroListEntrenadores.as_view(),name='seguro_entrenadores'),
    
    path('seguro_inscriptos/', SeguroListInscriptos.as_view(),name='seguro_inscriptos'),
  
    path('lista_kempes/', KempesList.as_view(),
         name='lista_kempes'),
    path('lista_agencia/', AgenciaList.as_view(),
         name='lista_agencia'),

   
    
  
    
]

urlpatterns += static(settings.MEDIA_URL, document_root= settings.MEDIA_ROOT)
