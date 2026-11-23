"""
Pruebas de los mails del sistema (confirmaciones, avisos, recuperar contraseña).
Correr con (PowerShell):  $env:LOCAL_SYNCDB="1"; python manage.py test apps.registro
"""
from datetime import date
from unittest import mock

from django.core import mail
from django.template.loader import render_to_string
from django.test import TestCase, override_settings

from apps.registro.correo import enviar_html, texto_plano

DATOS_INSCRIPCION = dict(
    persona='Gomez Laura', username='lgomez', email='l@x.com', eventoRelacionado='Triatlón de Prueba',
    distancia='Sprint', categoria='Elite', bici='Ruta', nombreEquipoPosta='', montoDebeAbonar=1000,
    montoAbonado=1000, fechaPago=date(2026, 11, 1), comentario='', obra_social='OSDE', responsable_tutor='Ana Gomez',
    relacion_legal='2', dni_responsable='20111222', mail_responsable='', telefono_responsable='351', password='abc123')

PLANTILLAS = {
    'email/bienvenida_inscripto.html': DATOS_INSCRIPCION,
    'email/alerta_admin_nuevoinscripto.html': DATOS_INSCRIPCION,
    'email/bienvenida_asociado.html': dict(persona='Gomez Laura', fecha=date(2026, 1, 1), tipoAsociado='Activo',
                                           fecha_emision_emmac=date(2000, 1, 1), numero_emmac='', entrenador='Juan',
                                           responsable_tutor='', montoDebeAbonar=1, montoAbonado=1,
                                           fechaPago=date(2026, 1, 1), comentario=''),
    'email/alerta_admin_PagoAsociado.html': dict(persona='Gomez Laura', cuota='Contado', fechaPago=date(2026, 1, 1),
                                                 montoAbonado=5, comentario=''),
    'email/alerta_admin_PagoEscuela.html': dict(asociado='Gomez Laura', opcion_elegida='Mensual', cuota='1',
                                                vencimiento=date(2026, 12, 31), monto_debe_abonar=1, monto_abonado=1,
                                                fecha_pago=date(2026, 1, 1), comentario=''),
    'registration/password_reset_email.html': dict(site_name='Triatlón Córdoba', user=None,
                                                    reset_link='https://portal.triatloncordoba.org/reset/AB/cd/'),
}


@override_settings(SITIO_URL='https://portal.triatloncordoba.org')
class CorreoTests(TestCase):

    def test_plantillas_livianas_sin_la_pagina_del_sitio(self):
        for plantilla, datos in PLANTILLAS.items():
            html = render_to_string(plantilla, datos)
            self.assertNotIn('<script', html, plantilla)        # antes mandaba el menu y los JS del sitio
            self.assertNotIn('sidebar', html, plantilla)
            self.assertIn('https://portal.triatloncordoba.org/static/registro/logo_triatloncba.png', html)
            self.assertLess(len(html), 15000, plantilla)

    def test_bienvenida_inscripto_datos(self):
        html = render_to_string('email/bienvenida_inscripto.html', DATOS_INSCRIPCION)
        for texto in ['Triatlón de Prueba', 'lgomez', 'abc123', 'Ana Gomez (madre)', '01/11/2026',
                      'href="https://portal.triatloncordoba.org/accounts/login/"']:
            self.assertIn(texto, html)
        self.assertNotIn('Equipo', html)   # sin equipo de posta no muestra la fila

    def test_reset_con_boton(self):
        html = render_to_string('registration/password_reset_email.html',
                                PLANTILLAS['registration/password_reset_email.html'])
        self.assertIn('href="https://portal.triatloncordoba.org/reset/AB/cd/"', html)

    def test_envia_html_y_texto(self):
        self.assertTrue(enviar_html('Hola', 'email/bienvenida_inscripto.html', DATOS_INSCRIPCION, ['a@x.com', 'a@x.com']))
        self.assertEqual(len(mail.outbox), 1)
        m = mail.outbox[0]
        self.assertEqual(m.to, ['a@x.com'])
        self.assertIn('Triatlón de Prueba', m.body)
        self.assertNotIn('<', m.body)
        self.assertEqual(m.alternatives[0][1], 'text/html')

    def test_si_gmail_falla_no_rompe(self):
        with mock.patch('django.core.mail.EmailMessage.send', side_effect=OSError('5.4.5 limit')), \
                self.assertLogs('apps.registro.correo', 'ERROR'):
            self.assertFalse(enviar_html('Hola', 'email/alerta_admin_PagoAsociado.html',
                                         PLANTILLAS['email/alerta_admin_PagoAsociado.html'], ['a@x.com']))

    def test_texto_plano(self):
        self.assertEqual(texto_plano('<style>x{}</style><p>Hola</p><p>chau <b>vos</b></p>'), 'Hola\nchau vos')
