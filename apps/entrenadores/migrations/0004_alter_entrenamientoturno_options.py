# Generated by Django 4.0.6 on 2023-05-05 18:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('entrenadores', '0003_remove_asignardiasentrenamiento_desde_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entrenamientoturno',
            options={'ordering': ['desde']},
        ),
    ]
