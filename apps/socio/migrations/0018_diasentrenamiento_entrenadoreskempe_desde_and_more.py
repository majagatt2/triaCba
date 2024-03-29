# Generated by Django 4.0.6 on 2023-04-25 17:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0017_remove_asociado_vigente_asociado_asiste'),
    ]

    operations = [
        migrations.CreateModel(
            name='DiasEntrenamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dias', models.CharField(max_length=50, verbose_name='Días')),
            ],
        ),
        migrations.AddField(
            model_name='entrenadoreskempe',
            name='desde',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entrenadoreskempe',
            name='hasta',
            field=models.TimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='entrenadoreskempe',
            name='dias',
            field=models.ManyToManyField(to='socio.diasentrenamiento', verbose_name='Dias'),
        ),
    ]
