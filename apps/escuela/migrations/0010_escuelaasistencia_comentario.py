# Generated by Django 4.0.6 on 2023-03-29 14:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('escuela', '0009_escuelaasistencia'),
    ]

    operations = [
        migrations.AddField(
            model_name='escuelaasistencia',
            name='comentario',
            field=models.CharField(blank=True, default='', max_length=100, null=True, verbose_name='Comentario'),
        ),
    ]