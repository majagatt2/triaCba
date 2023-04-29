# Generated by Django 4.0.6 on 2023-03-28 18:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('escuela', '0003_delete_escuelaasignacturno_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='EscuelaEntrenadores',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=40)),
                ('dni', models.IntegerField(blank=True, null=True)),
                ('nacionalidad', models.CharField(default='Argentina', max_length=12)),
                ('mail', models.EmailField(blank=True, max_length=254, null=True)),
                ('telefono', models.IntegerField(blank=True, default=0, null=True)),
                ('fecha_nacimiento', models.DateField(blank=True, null=True)),
                ('observacion', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='EscuelaFuncionesProfes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('funcion', models.CharField(max_length=8)),
                ('descricpcion', models.CharField(max_length=100)),
                ('desde', models.TimeField()),
                ('hasta', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='EscuelaTurnos',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=8)),
                ('cupo_turno', models.IntegerField()),
                ('desde', models.TimeField()),
                ('hasta', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='EscuelaAsignacTurno',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('habilitado', models.BooleanField(default=False)),
                ('seguro_escuela', models.BooleanField(default=False)),
                ('entrenador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escuela.escuelaentrenadores', verbose_name='Entrenador')),
                ('funcion', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escuela.escuelafuncionesprofes')),
                ('turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='escuela.escuelaturnos')),
            ],
        ),
    ]