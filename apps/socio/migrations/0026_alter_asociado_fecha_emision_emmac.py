# Generated by Django 4.0.6 on 2023-07-03 13:06

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0025_alter_asociado_fecha_emision_emmac'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociado',
            name='fecha_emision_emmac',
            field=models.DateField(blank=True, default=datetime.date(2000, 1, 1), null=True),
        ),
    ]
