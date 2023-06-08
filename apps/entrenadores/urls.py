from . import views
from apps.entrenadores.views import DiasAsignados
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth.decorators import login_required


urlpatterns = [
    path('horarios/', DiasAsignados.as_view(),
         name='horarios'),


]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
