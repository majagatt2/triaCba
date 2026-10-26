"""
Permisos sobre los datos de las personas.
Correr con (PowerShell):  $env:LOCAL_SYNCDB="1"; python manage.py test apps.usuarios
"""
from datetime import date

from django.test import TestCase, override_settings

from apps.usuarios.models import Persona


def persona(cuil, username, **extra):
    datos = dict(cuil=cuil, username=username, email=f'{username}@example.com', dni='1', domicilio='x', ciudad='x',
                 telefono='1', fechaNacimiento=date(1990, 1, 1), sexo='M', first_name='Nombre', last_name='Apellido')
    datos.update(extra)
    p = Persona(**datos)
    p.set_password('clave-segura-123')
    p.save()
    return p


@override_settings(SECURE_SSL_REDIRECT=False)
class PermisosPersonasTests(TestCase):

    def setUp(self):
        self.ana = persona('27111111117', 'ana')
        self.beto = persona('20222222223', 'beto')
        self.staff = persona('20333333334', 'staff', is_staff=True)

    def test_no_puede_editar_datos_de_otro(self):
        self.client.force_login(self.ana)
        self.assertEqual(self.client.get(f'/editar_usuarios/{self.beto.pk}/').status_code, 404)

    def test_puede_editar_sus_datos_sin_cambiar_cuil_ni_clave(self):
        self.client.force_login(self.ana)
        clave_antes = Persona.objects.get(pk=self.ana.pk).password
        r = self.client.post(f'/editar_usuarios/{self.ana.pk}/', {
            'cuil': '20999999990', 'first_name': 'Ana María', 'last_name': 'Apellido', 'username': 'ana',
            'email': 'ana@example.com', 'domicilio': 'x', 'ciudad': 'x', 'telefono': '1', 'fechaNacimiento': '1990-01-01',
            'nacionalidad': 'Argentina', 'sexo': 'F'})
        self.assertEqual(r.status_code, 302, r.context['form'].errors if r.context else '')
        ana = Persona.objects.get(pk=self.ana.pk)
        self.assertEqual(ana.first_name, 'Ana María')
        self.assertEqual(ana.password, clave_antes)
        self.assertFalse(Persona.objects.filter(pk='20999999990').exists())   # no se duplico la persona

    def test_staff_puede_editar_a_otros(self):
        self.client.force_login(self.staff)
        self.assertEqual(self.client.get(f'/editar_usuarios/{self.beto.pk}/').status_code, 200)

    def test_solo_staff_puede_eliminar(self):
        self.client.force_login(self.ana)
        self.client.post(f'/eliminar_usuarios/{self.beto.pk}/')
        self.assertTrue(Persona.objects.filter(pk=self.beto.pk).exists())
        self.client.force_login(self.staff)
        self.client.post(f'/eliminar_usuarios/{self.beto.pk}/')
        self.assertFalse(Persona.objects.filter(pk=self.beto.pk).exists())


@override_settings(SECURE_SSL_REDIRECT=False)
class IngresoTests(TestCase):

    def setUp(self):
        self.ana = persona('27111111117', '20d27d913', email='Ana.Perez@example.com')

    def ingresar(self, dato, clave='clave-segura-123'):
        return self.client.post('/accounts/login/', {'username': dato, 'password': clave})

    def test_ingresa_con_usuario_email_o_cuil(self):
        for dato in ['20d27d913', 'ana.perez@example.com', '27111111117', '27-11111111-7']:
            self.client.logout()
            r = self.ingresar(dato)
            self.assertEqual(r.status_code, 302, dato)

    def test_clave_incorrecta_muestra_error_en_la_tarjeta(self):
        r = self.ingresar('ana.perez@example.com', 'otra')
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, 'class="acceso-error"')
        self.assertContains(r, 'No pudimos ingresar')

    def test_vuelve_a_la_pagina_pedida(self):
        r = self.client.post('/accounts/login/', {'username': '20d27d913', 'password': 'clave-segura-123',
                                                  'next': '/inscripcion/mis_inscripciones/'})
        self.assertEqual(r['Location'], '/inscripcion/mis_inscripciones/')


@override_settings(SECURE_SSL_REDIRECT=False)
class CrearCuentaTests(TestCase):

    def datos(self, **cambios):
        from django.core.files.uploadedfile import SimpleUploadedFile
        d = {'cuil': '20301112220', 'first_name': 'Juana', 'last_name': 'Perez', 'username': 'juanap', 'email': 'j@example.com',
             'domicilio': 'x', 'ciudad': 'x', 'telefono': '1', 'fechaNacimiento': '1992-03-04', 'nacionalidad': 'Argentina',
             'sexo': 'F', 'password1': 'Clave-segura-123', 'password2': 'Clave-segura-123',
             'fotoDni': SimpleUploadedFile('dni.png', b'x' * 1000, content_type='image/png')}
        d.update(cambios)
        return d

    def test_al_crear_la_cuenta_entra_directo(self):
        r = self.client.post('/registro_usuarios/', self.datos())
        if r.status_code != 302:
            self.fail(r.context['form'].errors)
        self.assertEqual(r['Location'], '/registro/index')
        self.assertEqual(self.client.session['_auth_user_id'], '20301112220')   # quedo logueada

    def test_respeta_la_pagina_de_destino(self):
        r = self.client.post('/registro_usuarios/', self.datos(next='/inscripcion/inscribirme/7'))
        self.assertEqual(r['Location'], '/inscripcion/inscribirme/7')

    def test_no_redirige_a_otro_sitio(self):
        r = self.client.post('/registro_usuarios/', self.datos(next='https://sitio-malo.com/'))
        self.assertEqual(r['Location'], '/registro/index')

    def test_la_pagina_de_crear_cuenta_abre(self):
        self.assertEqual(self.client.get('/registro_usuarios/').status_code, 200)
        self.assertEqual(self.client.get('/registro_usuarios/?next=/inscripcion/eventos/').status_code, 200)
