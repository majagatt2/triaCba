# Generated by Django 4.0.6 on 2023-04-25 17:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('socio', '0018_diasentrenamiento_entrenadoreskempe_desde_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entrenadoreskempe',
            name='desde',
        ),
        migrations.RemoveField(
            model_name='entrenadoreskempe',
            name='dias',
        ),
        migrations.RemoveField(
            model_name='entrenadoreskempe',
            name='hasta',
        ),
        migrations.CreateModel(
            name='AsignarDiasEntrenamiento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('desde', models.TimeField(blank=True, null=True)),
                ('hasta', models.TimeField(blank=True, null=True)),
                ('dias', models.ManyToManyField(to='socio.diasentrenamiento', verbose_name='Dias')),
                ('entrenador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='socio.entrenadoreskempe', verbose_name='Entrenador')),
            ],
        ),
    ]