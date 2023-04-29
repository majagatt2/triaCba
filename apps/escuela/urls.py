from . import views
from apps.escuela.views import EscuelaPagosList, EscuelaPagoCreate, EscuelaAsistenciaCreate
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


urlpatterns = [

   
    path('lista_pagos_escuela/', login_required(EscuelaPagosList.as_view()),
         name='lista_pagos_escuela'),
    
    path('pagos_escuela/', login_required(EscuelaPagoCreate.as_view()), name='pagos_escuela'),
    
    path('asistencia/', login_required(EscuelaAsistenciaCreate.as_view()),
         name='asistencia'),


   



]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
