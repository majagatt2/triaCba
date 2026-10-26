from django import views
from django.urls import path, include
from . import views
from apps.socio.views import *
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


urlpatterns = [

    
    path('socios/', AsociadosList.as_view(), name='socios'),
    path('asociarse/', login_required(AsociadoCreate.as_view()), name='asociarse'),
    path('editar_socio/<pk>/', login_required(AsociadoEditar.as_view()), name='editar_socio'),
    path('pagos/', login_required(AsociadoPagoCreate.as_view()), name='pagos'),
    path('mensaje/', login_required(views.mensaje), name='mensaje'),
    
    path('lista_pagos_socio/', login_required(AsociadoPagosList.as_view()), name='lista_pagos_socio'),
    
    path('carnet/', login_required(AsociadoCertifList.as_view()), name='carnet'),
    
   

    
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)

handler404 = "apps.socio.views.error_404_view"
