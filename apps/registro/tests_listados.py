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
