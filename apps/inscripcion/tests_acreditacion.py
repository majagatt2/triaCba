"""
Pruebas de la pantalla de acreditacion (mesa del evento).
Correr con (PowerShell):  $env:LOCAL_SYNCDB="1"; python manage.py test apps.inscripcion
"""
from datetime import date, timedelta

from django.contrib.auth.models import Group
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.inscripcion.models import Eventos, Inscripcion
from apps.usuarios.models import Persona


@override_settings(SECURE_SSL_REDIRECT=False,
                   STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class AcreditacionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('datos_prueba', verbosity=0)
        cls.evento = Eventos.objects.get(nombreEvento='EVENTO DE PRUEBA')
        cls.evento.fechaEvento = date.today() + timedelta(days=2)
        cls.evento.save()
        cls.atleta = Persona.objects.get(cuil='20123456786')
        cls.atleta.last_name, cls.atleta.first_name, cls.atleta.dni = 'Gomez', 'Laura', '30111222'
        cls.atleta.save()
        cls.otro = Persona.objects.create_user(
            cuil='27888777666', username='otro', password='x', dni='28999000', domicilio='-', ciudad='-',
            telefono='-', fechaNacimiento=date(1985, 5, 5), first_name='Pedro', last_name='Diaz')
        cls.insc = Inscripcion.objects.create(
            persona=cls.atleta, eventoRelacionado=cls.evento, modalidad='Individual', distancia='Sprint',
            categoria='Elite', formaPago='1', montoDebeAbonar=1000, fechaPago=date.today(),
            obra_social='OSDE', emmac_file='media/eventos/emmac_certif/ok.png',
            control_pago=True, confirm_pago=True)
        cls.insc_otro = Inscripcion.objects.create(
            persona=cls.otro, eventoRelacionado=cls.evento, modalidad='Individual', distancia='Sprint',
            categoria='Elite', formaPago='1', montoDebeAbonar=1000, fechaPago=date.today(),
            obra_social='OSDE', numero=245)
        cls.voluntario = Persona.objects.create_user(
            cuil='20999888777', username='voluntario', password='x', dni='1', domicilio='-', ciudad='-',
            telefono='-', fechaNacimiento=date(1990, 1, 1), first_name='Vale')
        cls.voluntario.groups.add(Group.objects.get_or_create(name='Acreditador')[0])

    def url(self):
        return reverse('acreditacion_evento', args=[self.evento.pk])

    def test_atleta_comun_no_puede_entrar(self):
        self.client.force_login(self.atleta)
        r = self.client.get(reverse('acreditacion'))
        self.assertEqual(r.status_code, 302)
        r = self.client.get(self.url())
        self.assertEqual(r.status_code, 302)

    def test_sin_login_no_puede_entrar(self):
        r = self.client.get(reverse('acreditacion'))
        self.assertEqual(r.status_code, 302)

    def test_voluntario_ve_el_evento_en_la_lista(self):
        self.client.force_login(self.voluntario)
        r = self.client.get(reverse('acreditacion'))
        self.assertContains(r, 'EVENTO DE PRUEBA')
        self.assertContains(r, 'Acreditación')   # link en el menu lateral

    def test_buscar_por_dni_abre_la_ficha(self):
        self.client.force_login(self.voluntario)
        r = self.client.get(self.url(), {'q': '30111222'})
        self.assertContains(r, 'Gomez, Laura')
        self.assertContains(r, 'OK PARA ACREDITAR')

    def test_buscar_por_apellido(self):
        self.client.force_login(self.voluntario)
        r = self.client.get(self.url(), {'q': 'gome'})
        self.assertContains(r, 'Gomez, Laura')

    def test_ficha_con_observaciones(self):
        self.client.force_login(self.voluntario)
        r = self.client.get(self.url(), {'id': self.insc_otro.pk})
        self.assertContains(r, 'REVISAR')
        self.assertContains(r, 'NO aprobada')
        self.assertContains(r, 'Falta certificado')

    def test_acreditar_guarda_numero_quien_y_cuando(self):
        self.client.force_login(self.voluntario)
        r = self.client.post(self.url(), {'inscripcion': self.insc.pk, 'accion': 'acreditar',
                                          'numero': '17', 'chip': '9017'}, follow=True)
        self.assertContains(r, 'acreditado/a con el Nº 17')
        self.insc.refresh_from_db()
        self.assertTrue(self.insc.acreditacion)
        self.assertEqual((self.insc.numero, self.insc.numero_chip), (17, 9017))
        self.assertEqual(self.insc.acreditado_por, self.voluntario)
        self.assertIsNotNone(self.insc.acreditado_en)
        r = self.client.get(self.url(), {'id': self.insc.pk})
        self.assertContains(r, 'Ya acreditado')
        self.assertContains(r, 'por Vale')

    def test_numero_repetido_no_acredita(self):
        self.client.force_login(self.voluntario)
        r = self.client.post(self.url(), {'inscripcion': self.insc.pk, 'accion': 'acreditar',
                                          'numero': '245'}, follow=True)
        self.assertContains(r, 'ya lo tiene')
        self.insc.refresh_from_db()
        self.assertFalse(self.insc.acreditacion)

    def test_quitar_acreditacion(self):
        self.client.force_login(self.voluntario)
        self.client.post(self.url(), {'inscripcion': self.insc.pk, 'accion': 'acreditar', 'numero': '18'})
        self.client.post(self.url(), {'inscripcion': self.insc.pk, 'accion': 'deshacer'})
        self.insc.refresh_from_db()
        self.assertFalse(self.insc.acreditacion)
        self.assertIsNone(self.insc.acreditado_por)
        self.assertEqual(self.insc.numero, 18)   # el numero queda, por si se vuelve a acreditar

    def test_no_se_puede_acreditar_inscripcion_de_otro_evento(self):
        otro_evento = Eventos.objects.exclude(pk=self.evento.pk).first()
        if not otro_evento:
            self.skipTest('datos_prueba tiene un solo evento')
        self.client.force_login(self.voluntario)
        r = self.client.post(reverse('acreditacion_evento', args=[otro_evento.pk]),
                             {'inscripcion': self.insc.pk, 'accion': 'acreditar'})
        self.assertEqual(r.status_code, 404)

    def test_listado_para_acreditar_y_acreditados(self):
        self.client.force_login(self.voluntario)
        r = self.client.get(self.url(), {'ver': 'pendientes'})
        self.assertContains(r, 'Gomez, Laura')          # aprobada y sin acreditar
        self.assertNotContains(r, 'Diaz, Pedro')        # sin aprobar
        r = self.client.get(self.url(), {'ver': 'sinaprobar'})
        self.assertContains(r, 'Diaz, Pedro')
        self.client.post(self.url(), {'inscripcion': self.insc.pk, 'accion': 'acreditar', 'numero': '20'})
        r = self.client.get(self.url(), {'ver': 'acreditados'})
        self.assertContains(r, 'Gomez, Laura')
        self.assertContains(r, 'est-acreditado')

    def test_acreditar_desde_el_listado_vuelve_al_listado(self):
        self.client.force_login(self.voluntario)
        r = self.client.get(self.url(), {'id': self.insc.pk, 'ver': 'pendientes'})
        self.assertContains(r, 'Volver al listado')
        r = self.client.post(self.url(), {'inscripcion': self.insc.pk, 'accion': 'acreditar',
                                          'numero': '21', 'ver': 'pendientes', 'mod': ''})
        self.assertRedirects(r, self.url() + '?ver=pendientes#i%d' % self.insc.pk, fetch_redirect_response=False)

    def test_aprobar_solo_administrador(self):
        self.client.force_login(self.voluntario)
        r = self.client.get(self.url(), {'id': self.insc_otro.pk})
        self.assertNotContains(r, 'value="aprobar"')
        self.client.post(self.url(), {'inscripcion': self.insc_otro.pk, 'accion': 'aprobar'})
        self.insc_otro.refresh_from_db()
        self.assertFalse(self.insc_otro.confirm_pago)
        admin = Persona.objects.filter(is_staff=True).first() or self.voluntario
        admin.is_staff = True
        admin.save()
        self.client.force_login(admin)
        r = self.client.get(self.url(), {'id': self.insc_otro.pk})
        self.assertContains(r, 'value="aprobar"')
        self.client.post(self.url(), {'inscripcion': self.insc_otro.pk, 'accion': 'aprobar'})
        self.insc_otro.refresh_from_db()
        self.assertTrue(self.insc_otro.confirm_pago and self.insc_otro.control_pago)
