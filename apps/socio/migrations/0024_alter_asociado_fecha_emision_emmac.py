# Generated by Django 4.0.6 on 2023-07-03 12:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0023_alter_asociado_emmac_file_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociado',
            name='fecha_emision_emmac',
            field=models.DateField(blank=True, default=datetime.date(2000, 1, 1), null=True),
        ),
    ]
