from django.urls import path, include
from django import views
from . import views
from django.conf.urls.static import static
from apps.usuarios.views import UsuariosList, UsuariosUpdate, UsuariosCreate , UsuariosEliminar , DatosList
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required



urlpatterns = [

    #path('accounts/', include('django.contrib.auth.urls')),
    path('accounts/login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),

    path('password_reset/', PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html'), name='password_reset'),

    path('password_reset/done/', PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    
    path('registro_usuarios/', UsuariosCreate.as_view(), name='registro_usuarios'),
    path('lista_personas/', login_required(UsuariosList.as_view()),name='lista_personas'),
    path('datos_usuarios/', login_required(DatosList.as_view()), name='datos_usuarios'),
    path(r'editar_usuarios/<pk>/', login_required(UsuariosUpdate.as_view()),name='editar_usuarios'),
    path(r'eliminar_usuarios/<pk>/', login_required(UsuariosEliminar.as_view()), name='eliminar_usuarios'),
    

    

       
]
    
