# Generated by Django 3.2.15 on 2022-10-17 21:51

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0008_auto_20221015_1556'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociado',
            name='con_entrenador',
            field=models.CharField(choices=[('1', 'SI'), ('2', 'NO')], default=2, max_length=2, verbose_name='Entrenador? si/no - En el polo Kempes'),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='entrenador',
            field=models.ForeignKey(default=12, on_delete=django.db.models.deletion.CASCADE, to='socio.entrenadoreskempe', verbose_name='En el polo Kempes'),
        ),
        migrations.AlterField(
            model_name='asociado',
            name='obra_social',
            field=models.CharField(default='No informa', max_length=60),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='asociadopagos',
            name='tipoAsociadoPago',
            field=models.CharField(blank=True, max_length=40, null=True, verbose_name='Tipo Ascociado elegido:'),
        ),
    ]
