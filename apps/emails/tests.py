"""
Pruebas del modulo de emails masivos.
Correr con (PowerShell):  $env:LOCAL_SYNCDB="1"; python manage.py test apps.emails
"""
import shutil
import tempfile
from datetime import date, timedelta
from smtplib import SMTPDataError
from unittest import mock

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from apps.emails import envios
from apps.emails.models import EnvioEmail, Newsletter
from apps.usuarios.models import Persona

MEDIA_PRUEBA = tempfile.mkdtemp(prefix='media_emails_')


def persona(n, email, **extra):
    return Persona.objects.create_user(
        cuil=f'2077766{n:04d}', username=f'p{n}', password='x', dni=str(n), domicilio='-', ciudad='-',
        telefono='-', fechaNacimiento=date(1990, 1, 1), email=email, **extra)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend', SECURE_SSL_REDIRECT=False,
                   MEDIA_ROOT=MEDIA_PRUEBA, SITIO_URL='https://portal.triatloncordoba.org',
                   STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class EmailsTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin = persona(1, 'admin@example.com', is_staff=True)
        cls.atleta = persona(2, 'atleta@example.com')
        for n in range(3, 13):
            persona(n, f'persona{n}@example.com')
        persona(13, 'PERSONA3@example.com')   # repetido con otra mayuscula
        persona(14, 'no-es-un-mail')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_PRUEBA, ignore_errors=True)

    def nuevo(self, **extra):
        datos = dict(subject='Novedades', body='<p>Hola <img src="/media/uploads/foto.jpg"></p>',
                     email='triatloncba@gmail.com', bcc='Todas_las_Personas', status='Borrador')
        datos.update(extra)
        return Newsletter.objects.create(**datos)

    def test_solo_staff(self):
        self.client.force_login(self.atleta)
        self.assertEqual(self.client.get(reverse('create_email')).status_code, 403)
        self.assertEqual(self.client.get(reverse('desk_email')).status_code, 403)

    def test_destinatarios_sin_repetidos_ni_invalidos(self):
        emails = envios.emails_del_grupo('Todas_las_Personas')
        self.assertEqual(len([e for e in emails if e.lower() == 'persona3@example.com']), 1)
        self.assertNotIn('no-es-un-mail', emails)
        self.assertIn('triatloncba@gmail.com', emails)

    def test_un_mail_por_persona_con_imagen_absoluta_y_adjunto(self):
        n = self.nuevo()
        n.adjuntos.create(archivo=SimpleUploadedFile('flyer.png', b'png', content_type='image/png'))
        envios.encolar(n)
        r = envios.enviar_tanda(limite=5, pausa=0)
        self.assertEqual(r['enviados'], 5)
        self.assertEqual(len(mail.outbox), 5)
        m = mail.outbox[0]
        self.assertEqual(len(m.to), 1)
        self.assertFalse(m.bcc)
        html = m.alternatives[0][0]
        self.assertIn('src="https://portal.triatloncordoba.org/media/uploads/foto.jpg"', html)
        self.assertNotIn('sidebar', html)                         # ya no manda la pagina entera del sitio
        self.assertEqual(m.attachments[0][0], 'flyer.png')

    @override_settings()
    def test_respeta_limite_diario(self):
        n = self.nuevo()
        envios.encolar(n)
        with mock.patch.object(envios, 'LIMITE_DIARIO', 4):
            r = envios.enviar_tanda(pausa=0)
            self.assertEqual(r['enviados'], 4)
            r = envios.enviar_tanda(pausa=0)
            self.assertEqual(r['enviados'], 0)                    # cupo de 24 h agotado
        # pasado un dia vuelve a haber cupo
        EnvioEmail.objects.filter(estado=EnvioEmail.ENVIADO).update(enviado_en=timezone.now() - timedelta(hours=25))
        with mock.patch.object(envios, 'LIMITE_DIARIO', 4):
            self.assertEqual(envios.enviar_tanda(pausa=0)['enviados'], 4)

    def test_si_gmail_limita_se_frena_y_queda_pendiente(self):
        n = self.nuevo()
        envios.encolar(n)
        total = n.envios.count()
        error = SMTPDataError(550, b'5.4.5 Daily user sending limit exceeded')
        with mock.patch('django.core.mail.EmailMultiAlternatives.send', side_effect=error):
            r = envios.enviar_tanda(pausa=0)
        self.assertTrue(r['frenado_por_gmail'])
        self.assertEqual(n.envios.filter(estado=EnvioEmail.PENDIENTE).count(), total)

    def test_publicar_desde_el_formulario(self):
        self.client.force_login(self.admin)
        with mock.patch.object(envios, 'POR_TANDA', 3), mock.patch.object(envios, 'PAUSA', 0):
            r = self.client.post(reverse('create_email'), {
                'subject': 'Hola', 'body': '<p>texto</p>', 'email': 'triatloncba@gmail.com',
                'bcc': 'Todas_las_Personas', 'status': 'Publicar', 'accion': 'guardar',
                'adjuntos': [SimpleUploadedFile('a.pdf', b'%PDF', content_type='application/pdf')]})
        n = Newsletter.objects.get(subject='Hola')
        self.assertRedirects(r, reverse('detail_email', args=[n.pk]), fetch_redirect_response=False)
        self.assertEqual(n.adjuntos.count(), 1)
        p = envios.progreso(n)
        self.assertEqual(p['enviados'], 3)
        self.assertGreater(p['pendientes'], 0)
        self.assertEqual(len(mail.outbox), 3)

    def test_prueba_solo_a_mi(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('create_email'), {
            'subject': 'Prueba', 'body': '<p>x</p>', 'email': 'triatloncba@gmail.com', 'bcc': 'Todas_las_Personas',
            'status': 'Publicar', 'accion': 'prueba'})
        self.assertEqual([m.to for m in mail.outbox], [['admin@example.com']])
        n = Newsletter.objects.get(subject='Prueba')
        self.assertEqual(n.status, 'Borrador')
        self.assertFalse(n.envios.exists())

    def test_comando_programado(self):
        from django.core.management import call_command
        from io import StringIO
        n = self.nuevo()
        envios.encolar(n)
        salida = StringIO()
        with mock.patch.object(envios, 'PAUSA', 0):
            call_command('enviar_newsletters', cantidad=2, stdout=salida)
        self.assertIn('Enviados: 2', salida.getvalue())

    def test_prueba_a_otras_direcciones(self):
        self.client.force_login(self.admin)
        self.client.post(reverse('create_email'), {
            'subject': 'Prueba2', 'body': '<p>x</p>', 'email': 'triatloncba@gmail.com', 'bcc': 'Todas_las_Personas',
            'status': 'Publicar', 'accion': 'prueba', 'prueba_a': 'ale@x.com; pablo@x.com'})
        self.assertEqual([m.to for m in mail.outbox], [['ale@x.com'], ['pablo@x.com']])
        n = Newsletter.objects.get(subject='Prueba2')
        mail.outbox.clear()
        self.client.post(reverse('detail_email', args=[n.pk]), {'accion': 'prueba', 'prueba_a': 'no-es-un-mail'})
        self.assertEqual(mail.outbox, [])          # direccion invalida: no manda nada
        self.assertFalse(n.envios.exists())
