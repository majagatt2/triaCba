"""triaCba URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.views import LoginView
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
  
    path('escuela/', include('apps.escuela.urls')),
    path('registro/', include('apps.registro.urls')),
    path('asociado/', include('apps.socio.urls')),
    path('inscripcion/', include('apps.inscripcion.urls')),
    path('', include('apps.usuarios.urls')),
    path('entrenadores/', include('apps.entrenadores.urls')),
    
    # path('', LoginView.as_view(template_name='accounts/login.html'), name = 'login')
    
    
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "apps.socio.views.error_404_view"
handler404 = "apps.usuarios.views.error_404_view"
handler404 = "apps.inscripcion.views.error_404_view"
handler404 = "apps.registro.views.error_404_view"
