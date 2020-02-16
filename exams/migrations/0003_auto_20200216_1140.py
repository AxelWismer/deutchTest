# Generated by Django 2.2 on 2020-02-16 14:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('exams', '0002_auto_20200209_1736'),
    ]

    operations = [
        migrations.AddField(
            model_name='exam',
            name='valid',
            field=models.BooleanField(default=True, verbose_name='Examen valido'),
        ),
        migrations.AlterField(
            model_name='word',
            name='position',
            field=models.IntegerField(verbose_name='Posición'),
        ),
    ]