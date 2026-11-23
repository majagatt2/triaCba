from django.contrib import messages
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, TemplateView, View

from apps.emails import envios
from apps.emails.forms import NewsletterCreationForm
from apps.emails.models import EnvioEmail, Newsletter, NewsletterAdjunto
from apps.inscripcion.models import Eventos


def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


class SoloStaff(UserPassesTestMixin):
    """Antes cualquier usuario logueado podia entrar y mandar mails a todos."""
    def test_func(self):
        return self.request.user.is_staff


class DashboardHomeView(SoloStaff, TemplateView):
    template_name = "emails/desk_emails.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lista = list(Newsletter.objects.order_by('-created')[:30])
        for n in lista:
            n.progreso = envios.progreso(n)
            n.grupo = envios.nombre_del_grupo(n.bcc)
        context['newsletters'] = lista
        context['cupo'] = envios.cupo_disponible()
        context['limite_diario'] = envios.LIMITE_DIARIO
        context['por_tanda'] = envios.POR_TANDA
        context['pendientes'] = EnvioEmail.objects.filter(estado=EnvioEmail.PENDIENTE).count()
        return context

    def post(self, request, *args, **kwargs):
        if request.POST.get('accion') == 'tanda':
            r = envios.enviar_tanda()
            if r['frenado_por_gmail']:
                messages.warning(request, 'Gmail limitó los envíos por hoy. Lo pendiente sale automáticamente más adelante.')
            elif not r['cupo']:
                messages.warning(request, 'Se llegó al máximo de envíos de las últimas 24 horas. Lo pendiente sale automáticamente más adelante.')
            else:
                messages.success(request, f"Se enviaron {r['enviados']} mails ({r['errores']} con error). "
                                          f"Quedan {r['pendientes']} pendientes.")
        return redirect('desk_email')


class NewsletterCreateView(SoloStaff, CreateView):
    model = Newsletter
    template_name = "emails/form_email.html"
    form_class = NewsletterCreationForm
    success_url = reverse_lazy('desk_email')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['eventos'] = Eventos.objects.select_related('tipo').order_by('-fechaEvento')[:30]
        return kwargs

    def form_valid(self, form):
        newsletter = form.save(commit=False)
        newsletter.name = newsletter.subject[:250]
        prueba = self.request.POST.get('accion') == 'prueba'
        if prueba:
            newsletter.status = 'Borrador'
        newsletter.save()
        for archivo in form.archivos():
            NewsletterAdjunto.objects.create(newsletter=newsletter, archivo=archivo)

        if prueba:
            destino = self.request.user.email or envios.EMAIL_ASOCIACION
            try:
                envios.enviar_prueba(newsletter, destino)
                messages.success(self.request, f'Te mandamos una prueba a {destino}. Quedó guardado como borrador: '
                                               'revisalo y, si está bien, abrilo y enviálo al grupo.')
            except Exception as e:
                messages.error(self.request, f'No se pudo mandar la prueba: {e}')
            return redirect('detail_email', pk=newsletter.pk)

        if newsletter.status == 'Publicar':
            return _publicar(self.request, newsletter)
        messages.success(self.request, 'Guardado como borrador.')
        return redirect('detail_email', pk=newsletter.pk)


def _publicar(request, newsletter):
    nuevos = envios.encolar(newsletter)
    r = envios.enviar_tanda()
    p = envios.progreso(newsletter)
    texto = f'Email listo para {p["total"]} destinatarios. Ya se enviaron {p["enviados"]}.'
    if p['pendientes']:
        texto += (f' Los otros {p["pendientes"]} se envían solos, de a tandas, sin pasar el límite diario de Gmail '
                  f'(máximo {envios.LIMITE_DIARIO} cada 24 horas, para no bloquear los mails de inscripción).')
    if r['frenado_por_gmail']:
        messages.warning(request, texto + ' Gmail limitó los envíos por hoy.')
    else:
        messages.success(request, texto)
    return redirect('detail_email', pk=newsletter.pk)


class NewsletterDetailView(SoloStaff, View):
    def get(self, request, pk, *args, **kwargs):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        context = {
            'newsletter': newsletter,
            'progreso': envios.progreso(newsletter),
            'grupo': envios.nombre_del_grupo(newsletter.bcc),
            'errores': newsletter.envios.filter(estado=EnvioEmail.ERROR)[:50],
            'cuerpo': envios._urls_absolutas(newsletter.body),
            'destinatarios_estimados': None if newsletter.envios.exists() else
                len(envios._limpiar([newsletter.email] + envios.emails_del_grupo(newsletter.bcc))),
        }
        return render(request, 'emails/detail_emails.html', context)

    def post(self, request, pk, *args, **kwargs):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        accion = request.POST.get('accion')
        if accion == 'publicar':
            newsletter.status = 'Publicar'
            newsletter.save(update_fields=['status'])
            return _publicar(request, newsletter)
        if accion == 'prueba':
            destino = request.user.email or envios.EMAIL_ASOCIACION
            try:
                envios.enviar_prueba(newsletter, destino)
                messages.success(request, f'Te mandamos una prueba a {destino}.')
            except Exception as e:
                messages.error(request, f'No se pudo mandar la prueba: {e}')
        if accion == 'reintentar':
            n = newsletter.envios.filter(estado=EnvioEmail.ERROR).update(estado=EnvioEmail.PENDIENTE, error='')
            messages.success(request, f'{n} destinatarios con error vuelven a la cola.')
        return redirect('detail_email', pk=newsletter.pk)
