"""
Carnet digital del deportista federado.
Correr con (PowerShell):  $env:LOCAL_SYNCDB="1"; python manage.py test apps.socio
"""
import re
from datetime import date, timedelta

from django.test import TestCase, override_settings

from apps.socio.models import Asociado, AsociadoTipo, EntrenadoresKempe, EntrenamientoTurno
from apps.usuarios.models import Persona


@override_settings(SECURE_SSL_REDIRECT=False)
class CarnetTests(TestCase):

    def setUp(self):
        self.persona = Persona.objects.create(cuil='27111111117', username='ana', email='a@example.com', dni='30123456',
                                              first_name='ana', last_name='pérez', domicilio='x', ciudad='x', telefono='1',
                                              fechaNacimiento=date(1990, 1, 1), sexo='F')
        tipo = AsociadoTipo.objects.create(tipoAsociado='Activo', duracion=365)
        turno = EntrenamientoTurno.objects.create(nombre='M', cupo_turno=1, desde='07:00', hasta='08:00')
        EntrenadoresKempe.objects.create(id=12, nombre='Sin entrenador', turno=turno)
        self.asociado = Asociado.objects.create(persona=self.persona, fecha=date.today() - timedelta(days=30), tipoAsociado=tipo,
                                                obra_social='OSDE', estado=True, fecha_emision_emmac=date.today() - timedelta(days=10))
        self.client.force_login(self.persona)

    def url_qr(self):
        html = self.client.get('/asociado/carnet/').content.decode()
        return re.search(r'data-url="https?://[^/]+(/asociado/verificar/[^"]+)"', html).group(1)

    def test_carnet_vigente(self):
        r = self.client.get('/asociado/carnet/')
        self.assertContains(r, 'Deportista federado')
        self.assertContains(r, 'Ana Pérez')
        self.assertContains(r, 'DNI 30.123.456')
        self.assertContains(r, 'Vigente')
        self.assertContains(r, 'id="carnet-qr"')
        self.assertContains(r, 'id="carnet-reloj"')

    def test_qr_muestra_la_situacion_actual(self):
        url = self.url_qr()
        self.client.logout()                       # el que escanea no tiene cuenta
        r = self.client.get(url)
        self.assertContains(r, 'Verificación de carnet')
        self.assertContains(r, 'Vigente')
        # si despues vence, el mismo QR lo muestra vencido
        Asociado.objects.filter(pk=self.asociado.pk).update(fecha=date.today() - timedelta(days=400))
        self.assertContains(self.client.get(url), 'Vencido')

    def test_qr_falso(self):
        r = self.client.get('/asociado/verificar/inventado123/')
        self.assertEqual(r.status_code, 404)
        self.assertContains(r, 'Carnet no válido', status_code=404)

    def test_pago_pendiente(self):
        Asociado.objects.filter(pk=self.asociado.pk).update(estado=False)
        self.assertContains(self.client.get('/asociado/carnet/'), 'Pendiente de activación')

    def test_vencido_no_muestra_carnet(self):
        Asociado.objects.filter(pk=self.asociado.pk).update(fecha=date.today() - timedelta(days=400))
        r = self.client.get('/asociado/carnet/')
        self.assertContains(r, 'Tu período de federado venció')
        self.assertNotContains(r, 'id="carnet-qr"')

    def test_sin_asociacion(self):
        Asociado.objects.all().delete()
        self.assertContains(self.client.get('/asociado/carnet/'), 'Todavía no sos deportista federado')
