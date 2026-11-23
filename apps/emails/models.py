from django.db import models
from apps.usuarios.models import Persona
from ckeditor_uploader.fields import RichTextUploadingField

# Create your models here.


class Newsletter(models.Model):

    EMAIL_STATUS_CHOICES = (
        ('Borrador', "Borrador"),
        ('Publicar', 'Publicar')
    )

    name = models.CharField(max_length=250, default="", blank=True)
    subject = models.CharField(max_length=250)
    #body = models.TextField(blank=True, null=True)
    body = RichTextUploadingField(blank=True, null=True)
    email = models.CharField(("TO (email)"), max_length=250)
    bcc = models.CharField(("BCC"), max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=EMAIL_STATUS_CHOICES)

    def __str__(self):
        return self.name

    def get_email(self):
        return Persona.objects.filter(email=self)

    class Meta:
        ordering = ('-created',)


class NewsletterAdjunto(models.Model):
    """Archivo adjunto de un email masivo (imagen, PDF...). Va adjunto a cada envio."""
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='adjuntos')
    archivo = models.FileField(upload_to='emails/adjuntos/')

    def __str__(self):
        return self.archivo.name.rsplit('/', 1)[-1]


class EnvioEmail(models.Model):
    """Un destinatario de un email masivo. Los envios se hacen de a tandas (ver apps/emails/envios.py)
    para no pasar el limite diario de Gmail, que si se supera bloquea tambien los mails de inscripcion."""
    PENDIENTE, ENVIADO, ERROR = 'pendiente', 'enviado', 'error'
    ESTADOS = ((PENDIENTE, 'Pendiente'), (ENVIADO, 'Enviado'), (ERROR, 'Error'))

    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='envios')
    email = models.EmailField()
    estado = models.CharField(max_length=10, choices=ESTADOS, default=PENDIENTE, db_index=True)
    creado = models.DateTimeField(auto_now_add=True)
    enviado_en = models.DateTimeField(null=True, blank=True, db_index=True)
    error = models.TextField(blank=True, default='')

    class Meta:
        ordering = ('id',)
        constraints = [models.UniqueConstraint(fields=['newsletter', 'email'], name='envio_unico_por_email')]

    def __str__(self):
        return f'{self.email} ({self.estado})'
