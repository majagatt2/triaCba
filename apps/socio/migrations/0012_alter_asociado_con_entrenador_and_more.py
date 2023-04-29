# Generated by Django 4.0.6 on 2022-11-04 21:24

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0011_entrenadoreskempe_nacionalidad'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociado',
            name='con_entrenador',
            field=models.CharField(choices=[('1', 'SI'), ('2', 'NO')], default=2, max_length=2),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='emmac_file',
            field=models.ImageField(blank=True, null=True, upload_to='media/emmac'),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='entrenador',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='socio.entrenadoreskempe', verbose_name='Entrenador Kempes'),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='fecha_emision_emmac',
            field=models.DateField(default=datetime.date.today),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='relacion_legal',
            field=models.CharField(choices=[('1', '---------'), ('2', 'Madre'), ('3', 'Padre'), ('4', 'Tutor Legal')], default='', help_text='campo obligatorios en caso de ser menor de 18 años', max_length=2),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='tipoAsociado',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socio.asociadotipo'),
        ),
    ]