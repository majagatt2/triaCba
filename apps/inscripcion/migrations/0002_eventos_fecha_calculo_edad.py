# Generated by Django 4.0.6 on 2023-10-28 00:04

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inscripcion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='eventos',
            name='fecha_calculo_edad',
            field=models.DateField(default=datetime.date.today),
        ),
    ]
