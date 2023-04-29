# Generated by Django 3.2.15 on 2022-10-15 18:56

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0007_asociado_requisitos'),
    ]

    operations = [
        migrations.CreateModel(
            name='AsociadoREquisitos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('requisitos', ckeditor.fields.RichTextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='asociado',
            name='requisitos',
        ),
    ]
