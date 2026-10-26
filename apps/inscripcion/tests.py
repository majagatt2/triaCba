"""
Pruebas del proceso de inscripcion.
Correr con (PowerShell):  $env:LOCAL_SYNCDB="1"; python manage.py test apps.inscripcion
(usan una base temporal: no tocan la base local ni produccion)
"""
from datetime import date

from django.core import mail
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.inscripcion.models import EventoCosto, Eventos, Inscripcion
from apps.usuarios.models import Persona

CUIL_NUEVO = '20301112220'


def archivo(nombre, kb, tipo='image/png'):
    return SimpleUploadedFile(nombre, b'x' * (kb * 1024), content_type=tipo)


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
                   SECURE_SSL_REDIRECT=False, STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class InscripcionTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('datos_prueba', verbosity=0)
        cls.evento = Eventos.objects.get(nombreEvento='EVENTO DE PRUEBA')
        cls.costo = EventoCosto.objects.filter(evento=cls.evento, asociado='2').first()
        cls.atleta = Persona.objects.get(cuil='20123456786')

    def datos_inscripcion(self, **cambios):
        d = {
            'eventoRelacionado': self.evento.id, 'modalidad': 'Individual', 'categoria': 'Elite',
            'distancia': 'Sprint', 'bici': 'Ruta', 'obra_social': 'OSDE', 'formaPago': str(self.costo.id),
            'montoDebeAbonar': self.costo.precio, 'montoAbonado': self.costo.precio, 'fechaPago': '2026-10-20',
            'emmac_file': archivo('emmac.png', 300), 'comprobPago': archivo('pago.pdf', 200, 'application/pdf'),
        }
        d.update(cambios)
        return d

    def datos_persona(self, **cambios):
        d = {
            'cuil': CUIL_NUEVO, 'first_name': 'Juana', 'last_name': 'Perez', 'email': 'juana@example.com',
            'domicilio': 'Calle 1', 'ciudad': 'Cordoba', 'telefono': '3511111111', 'fechaNacimiento': '1992-03-04',
            'nacionalidad': 'Argentina', 'sexo': 'F', 'fotoDni': archivo('dni.png', 200),
        }
        d.update(cambios)
        return d

    # --- Tanda 1: lo que ve el atleta ---

    def test_formulario_publico_abre_sin_errores(self):
        r = self.client.get(reverse('inscripcion_publico', args=[self.evento.id]))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'errorlist')
        self.assertNotContains(r, 'errores-formulario')
        self.assertNotContains(r, 'alert("ESTIMADO')
        self.assertContains(r, 'inscripcion/js/archivos.js')

    def test_formulario_con_cuenta_abre_sin_errores(self):
        self.client.force_login(self.atleta)
        r = self.client.get(reverse('inscribirme', args=[self.evento.id]))
        self.assertEqual(r.status_code, 200)
        self.assertNotContains(r, 'errorlist')
        self.assertContains(r, 'data-inscripcion')

    def test_archivo_pesado_muestra_cuadro_de_errores_y_no_inscribe(self):
        datos = {**self.datos_persona(), **self.datos_inscripcion(emmac_file=archivo('emmac.png', 3 * 1024))}
        r = self.client.post(reverse('inscripcion_publico', args=[self.evento.id]), datos)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'errores-formulario')
        self.assertContains(r, 'todavía NO se registró')
        self.assertContains(r, 'tamaño máximo')
        self.assertEqual(Inscripcion.objects.count(), 0)

    def test_cuil_existente_explica_que_ingrese(self):
        datos = {**self.datos_persona(cuil='20123456786'), **self.datos_inscripcion()}
        r = self.client.post(reverse('inscripcion_publico', args=[self.evento.id]), datos)
        self.assertContains(r, 'Ya tenés una cuenta con este CUIL')

    def test_inscripcion_publica_completa(self):
        datos = {**self.datos_persona(), **self.datos_inscripcion()}
        r = self.client.post(reverse('inscripcion_publico', args=[self.evento.id]), datos)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Inscripcion.objects.filter(persona__cuil=CUIL_NUEVO).count(), 1)
        self.assertEqual(len(mail.outbox), 2)

    # --- Tanda 2: confirmacion rapida y segura ---

    def test_inscripcion_publica_lleva_a_pantalla_de_confirmacion(self):
        datos = {**self.datos_persona(), **self.datos_inscripcion()}
        r = self.client.post(reverse('inscripcion_publico', args=[self.evento.id]), datos, follow=True)
        self.assertContains(r, 'Tu inscripción quedó registrada')
        self.assertContains(r, 'Te enviamos un email')
        self.assertNotIn('triacba-2025', mail.outbox[1].body)

    def test_inscripcion_con_cuenta_lleva_a_pantalla_de_confirmacion(self):
        self.client.force_login(self.atleta)
        r = self.client.post(reverse('inscribirme', args=[self.evento.id]), self.datos_inscripcion(), follow=True)
        self.assertContains(r, 'Tu inscripción quedó registrada')
        self.assertEqual(Inscripcion.objects.filter(persona=self.atleta).count(), 1)

    def test_si_falla_el_email_la_inscripcion_igual_se_confirma(self):
        from unittest import mock
        self.client.force_login(self.atleta)
        with mock.patch('apps.inscripcion.views.EmailMessage.send', side_effect=OSError('550 Daily user sending limit exceeded')):
            r = self.client.post(reverse('inscribirme', args=[self.evento.id]), self.datos_inscripcion(), follow=True)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Tu inscripción quedó registrada')
        self.assertContains(r, 'no pudimos enviarte el email')
        self.assertEqual(Inscripcion.objects.filter(persona=self.atleta).count(), 1)

    def test_no_se_puede_ver_la_confirmacion_de_otro(self):
        otro = Persona.objects.create(cuil='27111111110', username='otro', email='o@example.com', dni='1',
                                      domicilio='x', ciudad='x', telefono='1', fechaNacimiento=date(1990, 1, 1), sexo='F')
        self.client.force_login(self.atleta)
        self.client.post(reverse('inscribirme', args=[self.evento.id]), self.datos_inscripcion())
        insc = Inscripcion.objects.get(persona=self.atleta)
        self.client.force_login(otro)
        self.assertEqual(self.client.get(reverse('inscripcion_recibida', args=[insc.pk])).status_code, 404)

    def test_mis_inscripciones_hace_pocas_consultas(self):
        # 40 inscripciones de otras personas no deben sumar consultas a la pagina del atleta
        for i in range(40):
            p = Persona.objects.create(cuil=f'2099{i:06d}0', username=f'p{i}', email=f'p{i}@example.com', dni='1',
                                       domicilio='x', ciudad='x', telefono='1', fechaNacimiento=date(1990, 1, 1), sexo='M')
            Inscripcion.objects.create(persona=p, eventoRelacionado=self.evento, formaPago='1', montoDebeAbonar=1,
                                       fechaPago=date(2026, 10, 1), obra_social='x')
        Inscripcion.objects.create(persona=self.atleta, eventoRelacionado=self.evento, formaPago='1', montoDebeAbonar=1,
                                   fechaPago=date(2026, 10, 1), obra_social='x')
        self.client.force_login(self.atleta)
        with self.assertNumQueries(4):  # sesion + usuario + inscripciones (con evento y tipo) + conteo
            r = self.client.get(reverse('mis_inscripciones'))
        self.assertEqual(r.status_code, 200)

    # --- Tanda 3: panel ---

    def test_admin_de_inscripciones_abre_y_busca(self):
        admin_user = Persona.objects.create_superuser(cuil='20222222223', username='admin_t', email='a@example.com',
                                                      password='x', dni='1', domicilio='x', ciudad='x', telefono='1',
                                                      fechaNacimiento=date(1980, 1, 1), sexo='M')
        self.client.force_login(admin_user)
        r = self.client.get('/admin/inscripcion/inscripcion/?q=Prueba')
        self.assertEqual(r.status_code, 200)

    # --- Cuenta existente al inscribirse sin cuenta ---

    def test_chequeo_de_cuil(self):
        r = self.client.get(reverse('cuil_registrado'), {'cuil': '20-12345678-6'})
        self.assertEqual(r.json(), {'existe': True})
        r = self.client.get(reverse('cuil_registrado'), {'cuil': CUIL_NUEVO})
        self.assertEqual(r.json(), {'existe': False})

    def test_cuil_existente_ofrece_ingresar_y_seguir(self):
        datos = {**self.datos_persona(cuil='20123456786'), **self.datos_inscripcion()}
        r = self.client.post(reverse('inscripcion_publico', args=[self.evento.id]), datos)
        html = r.content.decode()
        self.assertIn('id="cuenta-existente"', html)
        self.assertNotIn('data-url-chequeo="/inscripcion/cuil_registrado/" hidden', html)   # la caja se ve
        self.assertIn(f'/accounts/login/?next=/inscripcion/inscribirme/{self.evento.id}', html.replace('%2F', '/'))

    def test_login_desde_inscripcion_explica_y_vuelve_al_formulario(self):
        destino = reverse('inscribirme', args=[self.evento.id])
        r = self.client.get('/accounts/login/', {'next': destino})
        self.assertContains(r, 'seguís con tu inscripción')
        r = self.client.post('/accounts/login/', {'username': 'atleta.prueba@example.com', 'password': 'prueba1234', 'next': destino})
        self.assertEqual(r['Location'], destino)

    # --- Menores de 18 ---

    def test_menor_sin_datos_del_responsable_no_se_inscribe(self):
        datos = {**self.datos_persona(fechaNacimiento='2012-05-01'), **self.datos_inscripcion()}
        r = self.client.post(reverse('inscripcion_publico', args=[self.evento.id]), datos)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'Sos menor de 18 años')
        self.assertContains(r, 'Completá el nombre y apellido de tu madre, padre o tutor.')
        self.assertNotContains(r, 'id="panel-menores" data-fecha-evento="%s" hidden' % self.evento.fechaEvento.isoformat())
        self.assertEqual(Inscripcion.objects.count(), 0)

    def test_menor_con_datos_del_responsable_se_inscribe(self):
        datos = {**self.datos_persona(fechaNacimiento='2012-05-01'),
                 **self.datos_inscripcion(responsable_tutor='Ana Perez', relacion_legal='2', dni_responsable='20111222',
                                          telefono_responsable='3511234567')}
        r = self.client.post(reverse('inscripcion_publico', args=[self.evento.id]), datos)
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Inscripcion.objects.get().responsable_tutor, 'Ana Perez')

    def test_menor_con_cuenta_ve_la_seccion_y_es_obligatoria(self):
        menor = Persona.objects.create(cuil='20444444445', username='menor', email='m@example.com', dni='1', domicilio='x',
                                       ciudad='x', telefono='1', fechaNacimiento=date(2012, 5, 1), sexo='M')
        self.client.force_login(menor)
        r = self.client.get(reverse('inscribirme', args=[self.evento.id]))
        self.assertContains(r, 'Sos menor de 18 años')
        r = self.client.post(reverse('inscribirme', args=[self.evento.id]), self.datos_inscripcion())
        self.assertEqual(r.status_code, 200)
        self.assertEqual(Inscripcion.objects.filter(persona=menor).count(), 0)

    def test_mayor_con_cuenta_no_ve_la_seccion(self):
        self.client.force_login(self.atleta)
        self.assertNotContains(self.client.get(reverse('inscribirme', args=[self.evento.id])), 'Sos menor de 18 años')
