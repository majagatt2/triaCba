# Generated by Django 3.2.15 on 2022-10-25 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0009_auto_20221017_1851'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociadopagos',
            name='opcionElegida',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='socio.asociadocosto', verbose_name='Referencia para elegir opciones de pago:'),
        ),
    ]