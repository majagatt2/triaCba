# Generated by Django 4.0.6 on 2023-05-16 15:42

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0022_alter_asociado_emmac_file'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociado',
            name='emmac_file',
            field=models.ImageField(blank=True, default='media/emmac/Sin_emmac.png', null=True, upload_to='media/emmac'),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='fecha_emision_emmac',
            field=models.DateField(blank=True, default=datetime.date(2000, 1, 1)),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='numero_emmac',
            field=models.CharField(blank=True, default='s/d', max_length=10, verbose_name='numero Emmac'),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='relacion_legal',
            field=models.CharField(blank=True, choices=[('1', 'Madre'), ('2', 'Padre'), ('3', 'Tutor Legal')], default='1', help_text='campo obligatorios en caso de ser menor de 18 años', max_length=2),
        ),
    ]
