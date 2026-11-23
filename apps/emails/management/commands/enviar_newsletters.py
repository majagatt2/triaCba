"""
Envia la proxima tanda de emails masivos pendientes.

Una tanda:            python manage.py enviar_newsletters
Siempre encendido:    python manage.py enviar_newsletters --cada-minutos 60
  (para una "Always-on task" de PythonAnywhere: el plan actual no tiene tareas programadas por hora;
   asi el mismo proceso manda una tanda, espera una hora y repite. Si se cae, PythonAnywhere lo reinicia.)
"""
import time

from django.core.management.base import BaseCommand
from django.db import close_old_connections

from apps.emails.envios import enviar_tanda


class Command(BaseCommand):
    help = 'Envia la proxima tanda de emails masivos pendientes (respetando el limite diario).'

    def add_arguments(self, parser):
        parser.add_argument('--cantidad', type=int, default=None, help='Maximo de mails en esta tanda.')
        parser.add_argument('--cada-minutos', type=int, default=0,
                            help='Repetir para siempre: una tanda, esperar estos minutos, otra tanda...')

    def tanda(self, cantidad):
        close_old_connections()   # en un proceso que dura dias, la conexion a la base se renueva cada vez
        try:
            r = enviar_tanda(limite=cantidad)
        except Exception as e:     # un error (base caida, etc.) no termina el proceso siempre encendido
            self.stderr.write(f'Error en la tanda: {e}')
            return
        if r['enviados'] or r['errores'] or r['frenado_por_gmail'] or not self.repetir:
            self.stdout.write(
                f"{time.strftime('%d/%m %H:%M')} Enviados: {r['enviados']} · errores: {r['errores']}"
                f" · quedan pendientes: {r['pendientes']} · cupo de esta tanda: {r['cupo']}"
                + (' · GMAIL LIMITO LOS ENVIOS' if r['frenado_por_gmail'] else ''))
            self.stdout.flush()

    def handle(self, *args, **opciones):
        self.repetir = opciones['cada_minutos'] > 0
        self.tanda(opciones['cantidad'])
        while self.repetir:
            time.sleep(opciones['cada_minutos'] * 60)
            self.tanda(opciones['cantidad'])
