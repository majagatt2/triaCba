"""
Envia la proxima tanda de emails masivos pendientes.
Se programa en PythonAnywhere (pestaña Tasks) para que corra cada hora:
    cd ~/triaCba && ~/.virtualenvs/triatlon/bin/python manage.py enviar_newsletters
"""
from django.core.management.base import BaseCommand

from apps.emails.envios import enviar_tanda


class Command(BaseCommand):
    help = 'Envia la proxima tanda de emails masivos pendientes (respetando el limite diario).'

    def add_arguments(self, parser):
        parser.add_argument('--cantidad', type=int, default=None, help='Maximo de mails en esta tanda.')

    def handle(self, *args, **opciones):
        r = enviar_tanda(limite=opciones['cantidad'])
        self.stdout.write(
            f"Enviados: {r['enviados']} · errores: {r['errores']} · quedan pendientes: {r['pendientes']}"
            f" · cupo de esta tanda: {r['cupo']}" + (' · GMAIL LIMITO LOS ENVIOS' if r['frenado_por_gmail'] else ''))
