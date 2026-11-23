"""
Pruebas de los listados de Administracion y de las miniaturas del Admin.
Correr con (PowerShell):  $env:LOCAL_SYNCDB="1"; python manage.py test apps.registro
"""
import io
import shutil
import tempfile
from datetime import date, timedelta

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.urls import reverse

from apps.inscripcion.models import Eventos, Inscripcion
from apps.registro.miniaturas import miniatura_html, miniatura_url
from apps.usuarios.models import Persona

MEDIA_PRUEBA = tempfile.mkdtemp(prefix='media_prueba_')


@override_settings(SECURE_SSL_REDIRECT=False, MEDIA_ROOT=MEDIA_PRUEBA,
                   STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ListadosTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('datos_prueba', verbosity=0)
        cls.evento = Eventos.objects.get(nombreEvento='EVENTO DE PRUEBA')
        cls.evento.fechaEvento = date.today() + timedelta(days=5)
        cls.evento.save()
        cls.admin = Persona.objects.create_user(
            cuil='20555444333', username='admin_listados', password='x', dni='1', domicilio='-', ciudad='-',
            telefono='-', fechaNacimiento=date(1980, 1, 1), is_staff=True, is_superuser=True)
        datos = dict(eventoRelacionado=cls.evento, modalidad='Individual', distancia='Sprint', categoria='Elite',
                     formaPago='1', montoDebeAbonar=1000, montoAbonado=1000, fechaPago=date.today(), obra_social='OSDE')
        cls.personas = []
        for n, (ap, aprobado, acreditado) in enumerate([('Zapata', False, False), ('Alvarez', True, False),
                                                       ('Benitez', True, True)]):
            p = Persona.objects.create_user(cuil=f'2011122233{n}', username=f'u{n}', password='x', dni=f'4000000{n}',
                                            last_name=ap, first_name='Ana', domicilio='-', ciudad='Cba',
                                            telefono='-', fechaNacimiento=date(1990, 1, 1), sexo='F')
            Inscripcion.objects.create(persona=p, confirm_pago=aprobado, acreditacion=acreditado,
                                       numero=10 + n if acreditado else 0, **datos)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(MEDIA_PRUEBA, ignore_errors=True)

    def setUp(self):
        self.client.force_login(self.admin)

    def url(self, **params):
        return reverse('lista_inscriptos_admin', args=[self.evento.pk])

    def test_pendientes_primero_y_filtros(self):
        r = self.client.get(self.url())
        html = r.content.decode()
        self.assertLess(html.index('Zapata'), html.index('Alvarez'))   # el pendiente arriba aunque sea "Z"
        self.assertContains(r, 'Pendientes de aprobar <b>1</b>', html=False)
        r = self.client.get(self.url(), {'estado': 'pendientes'})
        self.assertContains(r, 'Zapata')
        self.assertNotContains(r, 'Alvarez')
        r = self.client.get(self.url(), {'estado': 'acreditados'})
        self.assertContains(r, 'Benitez')
        self.assertNotContains(r, 'Zapata')

    def test_link_editar_en_admin(self):
        insc = Inscripcion.objects.get(persona__last_name='Zapata')
        r = self.client.get(self.url())
        self.assertContains(r, reverse('admin:inscripcion_inscripcion_change', args=[insc.pk]))

    def test_exportar_excel(self):
        from openpyxl import load_workbook
        r = self.client.get(self.url(), {'exportar': 'xlsx', 'estado': 'aprobados'})
        self.assertEqual(r['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.assertIn('attachment;', r['Content-Disposition'])
        hoja = load_workbook(io.BytesIO(r.content)).active
        apellidos = [f[2] for f in hoja.iter_rows(min_row=2, values_only=True)]
        self.assertEqual(apellidos, ['Alvarez'])
        self.assertEqual(hoja['A1'].value, 'Nº corredor')

    def test_lista_eventos_proximos_primero_con_pendientes(self):
        pasado = Eventos.objects.exclude(pk=self.evento.pk).first()
        if pasado:
            pasado.fechaEvento = date.today() - timedelta(days=30)
            pasado.save()
        r = self.client.get(reverse('lista_eventos'))
        self.assertContains(r, 'Próximo')
        self.assertContains(r, f'{self.url()}?estado=pendientes')
        filas = r.context['filas']
        self.assertTrue(filas[0]['proximo'])
        fila = next(f for f in filas if f['evento'] == self.evento)
        self.assertEqual((fila['total'], fila['pendientes'], fila['acreditados']), (3, 1, 1))

    def test_miniatura_liviana(self):
        from PIL import Image
        insc = Inscripcion.objects.get(persona__last_name='Zapata')
        buf = io.BytesIO()
        Image.new('RGB', (2000, 1500), (200, 30, 30)).save(buf, 'JPEG')
        insc.emmac_file.save('certificado.jpg', ContentFile(buf.getvalue()), save=True)
        url = miniatura_url(insc.emmac_file)
        self.assertTrue(url.startswith('/media/miniaturas/'))
        with Image.open(MEDIA_PRUEBA + url[len('/media'):]) as mini:
            self.assertLessEqual(max(mini.size), 120)
        self.assertEqual(miniatura_url(insc.emmac_file), url)          # la segunda vez reutiliza la misma
        html = miniatura_html(insc.emmac_file)
        self.assertIn(url, html)
        self.assertIn(insc.emmac_file.url, html)                          # el link abre el original
        insc.comprobPago.save('pago.pdf', ContentFile(b'%PDF-1.4'), save=True)
        self.assertIn('PDF', miniatura_html(insc.comprobPago))


@override_settings(SECURE_SSL_REDIRECT=False, MEDIA_ROOT=MEDIA_PRUEBA,
                   STATICFILES_STORAGE='django.contrib.staticfiles.storage.StaticFilesStorage')
class ListadosSociosTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        call_command('datos_prueba', verbosity=0)
        cls.admin = Persona.objects.create_user(
            cuil='20555444334', username='admin_socios', password='x', dni='2', domicilio='-', ciudad='-',
            telefono='-', fechaNacimiento=date(1980, 1, 1), is_staff=True, is_superuser=True)
        # persona sin foto de perfil ni DNI: antes daba error 500 en la lista de personas y en todo el sitio
        Persona.objects.filter(pk=cls.admin.pk).update(fotoPerfil='', fotoDni='')

    def setUp(self):
        self.client.force_login(self.admin)

    def test_paginas_de_administracion_responden(self):
        for nombre in ['lista_personas', 'lista_asociados', 'lista_asociados_asamblea', 'lista_entrenadores',
                       'lista_pagos_socios', 'cta_cte_socios', 'resumen', 'estad_escuela', 'desk_email',
                       'create_email', 'lista_eventos']:
            r = self.client.get(reverse(nombre))
            self.assertEqual(r.status_code, 200, nombre)

    def test_excel_de_socios_solo_staff(self):
        r = self.client.get(reverse('lista_asociados'), {'exportar': 'xlsx'})
        self.assertEqual(r['Content-Type'], 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        self.client.logout()
        r = self.client.get(reverse('lista_asociados_asamblea'), {'exportar': 'xlsx'})
        self.assertEqual(r.status_code, 403)

    def test_pagos_socios_recientes_primero(self):
        from apps.socio.models import AsociadoPagos
        p = Persona.objects.exclude(pk=self.admin.pk).first()
        AsociadoPagos.objects.create(personaAsociada=p, fechaPago=date(2025, 1, 1), montoAbonado=1, montoDebeAbonar=1)
        AsociadoPagos.objects.create(personaAsociada=p, fechaPago=date(2026, 6, 1), montoAbonado=None, montoDebeAbonar=None)
        r = self.client.get(reverse('lista_pagos_socios'))
        fechas = [c.fechaPago for c in r.context['asociadopagos_list']]
        self.assertEqual(fechas, sorted(fechas, reverse=True))
        r = self.client.get(reverse('lista_pagos_socios'), {'anio': '2025'})
        self.assertTrue(all(c.fechaPago.year == 2025 for c in r.context['asociadopagos_list']))

    def test_lista_personas_de_ambas_direcciones(self):
        # /lista_personas/ (la del menu) daba error 500 con una persona sin CUIL
        Persona.objects.create_user(cuil='', username='sin_cuil', password='x', dni='9', domicilio='-',
                                    ciudad='-', telefono='-', fechaNacimiento=date(1980, 1, 1))
        for url in ['/lista_personas/', '/registro/lista_personas/']:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200, url)
