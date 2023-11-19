from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.contrib.auth.decorators import login_required
from .views import DashboardHomeView, NewsletterCreateView, NewsletterDetailView

urlpatterns = [

    path('desk_email/', login_required(DashboardHomeView.as_view()),
         name='desk_email'),
    path('create_email/',
         login_required(NewsletterCreateView.as_view()), name='create_email'),

    path('detail_email/<pk>',
         login_required(NewsletterDetailView.as_view()), name='detail_email'),


]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)
