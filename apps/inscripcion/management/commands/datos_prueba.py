"""
Crea un evento de prueba con todo lo necesario para inscribirse, y un atleta de prueba.
Solo funciona con la base local SQLite (DB_LOCAL_SQLITE=1): nunca toca produccion.

Uso:  python manage.py datos_prueba
"""
from datetime import date, timedelta

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.inscripcion.models import (
    EventoBici, EventoCategoria, EventoCosto, EventoDistancia, EventoFormasPago,
    EventoModalidade, Eventos, EventoTipo, ModalidadEventos,
)
from apps.usuarios.models import Persona


class Command(BaseCommand):
    help = 'Crea datos de prueba para inscripciones (solo base local).'

    def handle(self, *args, **options):
        motor = settings.DATABASES['default']['ENGINE']
        if 'sqlite3' not in motor:
            raise CommandError('Este comando solo corre con la base local SQLite (DB_LOCAL_SQLITE=1).')

        tipo, _ = EventoTipo.objects.get_or_create(tipoEvento='Triatlón')
        hoy = date.today()
        evento, creado = Eventos.objects.get_or_create(
            nombreEvento='EVENTO DE PRUEBA',
            defaults=dict(
                año=hoy.year, fechaEvento=hoy + timedelta(days=30), fecha_calculo_edad=date(hoy.year, 12, 31),
                temporada=f'{hoy.year}', tipo=tipo, lugar='ALMAFUERTE', cupo=300, estado=True,
                contenido='<p>Evento creado para pruebas locales.</p>', inscribirse=True,
            ),
        )
        modalidad, _ = EventoModalidade.objects.get_or_create(modalidad='Individual')
        me, _ = ModalidadEventos.objects.get_or_create(evento=evento, modalidad=modalidad)
        for nombre in ['Sprint', 'Standard']:
            me.distancia_disponible.add(EventoDistancia.objects.get_or_create(distancia=nombre)[0])
        for nombre in ['Elite', 'Promocional']:
            me.categoria_disponible.add(EventoCategoria.objects.get_or_create(categoria=nombre)[0])
        for nombre in ['Ruta', 'MTB']:
            me.bici_disponible.add(EventoBici.objects.get_or_create(bici=nombre)[0])
        transferencia, _ = EventoFormasPago.objects.get_or_create(formaPago='Transferencia')
        EventoCosto.objects.get_or_create(evento=evento, asociado='2', formaPago=transferencia, defaults={'precio': 25000})
        EventoCosto.objects.get_or_create(evento=evento, asociado='1', formaPago=transferencia, defaults={'precio': 18000})

        if not Persona.objects.filter(cuil='20123456786').exists():
            atleta = Persona(cuil='20123456786', dni='12345678', username='atleta_prueba', first_name='Atleta',
                             last_name='Prueba', email='atleta.prueba@example.com', domicilio='Calle 123',
                             ciudad='Córdoba', telefono='3510000000', fechaNacimiento=date(1990, 5, 10),
                             nacionalidad='Argentina', sexo='M')
            atleta.set_password('prueba1234')
            atleta.save()

        self.stdout.write(self.style.SUCCESS(
            f'Listo. Evento de prueba: id {evento.id}\n'
            f'  Formulario sin cuenta:  /inscripcion/inscripcion_publico/{evento.id}\n'
            f'  Formulario con cuenta:  /inscripcion/inscribirme/{evento.id}  (usuario atleta_prueba / prueba1234)'
        ))
