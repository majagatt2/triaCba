from django.shortcuts import get_object_or_404, render
from django.views.generic import TemplateView,  View,  CreateView
from apps.emails.models import Newsletter
from apps.emails.forms import NewsletterCreationForm
from apps.usuarios.models import Persona
from apps.socio.models import Asociado
from apps.inscripcion.models import Eventos, Inscripcion
from django.conf import settings
from django.core.mail import  EmailMessage
from django.contrib.messages.views import SuccessMessageMixin
from django.template.loader import render_to_string
import time

from django.urls import reverse_lazy


# Create your views here.

def error_404_view(request, exception):
    return render(request, 'base/pages-error-404.html')


class DashboardHomeView(TemplateView):
    template_name = "emails/desk_emails.html"



class NewsletterCreateView(SuccessMessageMixin,CreateView):
    model = Newsletter
    template_name = "emails/form_email.html"
    form_class = NewsletterCreationForm
    success_url = reverse_lazy("create_email")
    success_message = "El email se envió con éxito !"

    def cargar_listas(self):
        # Se calcula en cada pedido. Antes estaba en el cuerpo de la clase y se
        # calculaba una sola vez al arrancar el servidor (listas desactualizadas).
        self.tournaments = list(Eventos.objects.values_list('id', flat=True))
        self.email_members = []
        self.email_members_con_acceso = []
        self.email_escuela = []
        self.email_people_all = ['triatloncba@gmail.com']

        for m in Asociado.objects.filter():
            if m.get_estado == True:
                if m.persona.email in self.email_members:
                    pass
                else:
                    self.email_members.append(m.persona.email)

        for m in Asociado.objects.filter(tipoAsociado = 1):
            if m.get_estado == True:
                if m.persona.email in self.email_members_con_acceso:
                    pass
                else:
                    self.email_members_con_acceso.append(m.persona.email)

        for m in Asociado.objects.filter(tipoAsociado = 5):
            if m.get_estado == True and m.asiste == True:
                if m.persona.email in self.email_escuela:
                    pass
                else:
                    self.email_escuela.append(m.persona.email)

        for p in Persona.objects.all():
            if p.email in self.email_people_all or p.email == "" :
                pass
            else:
                self.email_people_all.append(p.email)



    def get_context_data(self, **kwargs):
        context = super(NewsletterCreateView,
                        self).get_context_data(**kwargs)
        self.cargar_listas()

        groups = []

        for n in range(1):
            groups.insert(1,'Asociados')
        for n in range(1):
            groups.insert(2, 'Asociados_Escuela')
        for n in range(1):
            groups.insert(3, 'Asociados_con_acceso_Kempes')
        for n in range(1):
            groups.insert(4, 'Todas_las_Personas')


        for n in range(1):
            groups.insert(0, 'Nadie')




        all = self.email_people_all
        context['all'] = all
        context['groups'] = groups
        context['tournament'] = Eventos.objects.all()
        return context

    def form_valid(self, form, **kwargs):
        self.cargar_listas()
        instance = form.save()

        if instance.status == "Publicar":
            template = render_to_string(
                'emails/email.html', {'body': instance.body})
            try:
                instance_bcc = int(instance.bcc)
                print(f'instance_bcc: {instance_bcc}')
            except ValueError:
                instance_bcc = instance.bcc
                print(f'instance_bcc: {instance_bcc}')

            subject = instance.subject
            body = instance.body
            from_email = settings.EMAIL_HOST_USER

            if instance_bcc == "Asociados":
                to = [instance.email]
                bcc = self.email_members
                print("emails members")

            elif type(instance_bcc) == int:
                emails_tournament = []
                for t in self.tournaments:

                    if t == instance_bcc:
                        for r in Inscripcion.objects.filter(eventoRelacionado=t):
                            print(r.persona.email)
                            emails_tournament.append(r.persona.email)
                to = [instance.email]
                bcc = emails_tournament
            elif instance_bcc == "Nadie":
                to = [instance.email]
                bcc = []
            elif instance_bcc == "Todas_las_Personas":
                to = [instance.email]
                bcc = self.email_people_all

            elif instance_bcc == "Asociados_con_acceso_Kempes":
                to = [instance.email]
                bcc = self.email_members_con_acceso

            elif instance_bcc == "Asociados_Escuela":
                to = [instance.email]
                bcc = self.email_escuela



            quatity = 50
            blocks = int(len(bcc)/quatity)
            print(f'blocks: {blocks}')

            bcc_by_block = []

            for n in range(blocks):
                print(n)
                bcc_by_block.append(bcc[n*quatity:(n+1)*quatity])

            if len(bcc) % quatity:
                bcc_by_block.append(bcc[blocks*quatity:])

            #print(bcc_by_block)
            #time.sleep(5)


            print(f'tipo instancia {type(instance.email)}')
            print(f'instancia {instance.email}')
            print(f'enviado a {to}')
            #print(f'enviado BCC a {bcc}')

            if len(bcc_by_block) > 0:
                for m in range(len(bcc_by_block)):
                    print(f'cantidad bloque {m}: {len(bcc_by_block[m])}')
                    print(bcc_by_block[m])
                    msg = EmailMessage(subject, template, from_email, to, bcc=bcc_by_block[m])
                    msg.content_subtype = "html"
                    msg.fail_silently = False
                    msg.send()
                    print('TIME 5seg')
                    time.sleep(5)
            else:
                msg = EmailMessage(subject, template,
                                   from_email, to, bcc=bcc_by_block)
                msg.content_subtype = "html"
                msg.fail_silently = False
                msg.send()
        else:
            print("no published")

        return super().form_valid(form)






class NewsletterDetailView(View):
    def get(self, request, pk, *args, **kwargs):
        newsletter = get_object_or_404(Newsletter, pk=pk)
        context = {
            'newsletter': newsletter
        }
        return render(request, 'emails/desk_emails.html', context)




