# Generated by Django 4.0.6 on 2023-05-10 13:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0021_asociado_numero_emmac'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociado',
            name='emmac_file',
            field=models.ImageField(blank=True, default='Foto emmac', null=True, upload_to='media/emmac'),
        ),
    ]
