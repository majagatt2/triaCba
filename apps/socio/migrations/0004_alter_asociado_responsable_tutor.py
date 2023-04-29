# Generated by Django 3.2.15 on 2022-10-14 20:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0003_alter_asociado_telefono_responsable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='asociado',
            name='responsable_tutor',
            field=models.CharField(blank=True, default='', help_text='campos obligatorios en caso de ser menor de 18 años', max_length=40, null=True),
        ),
    ]
