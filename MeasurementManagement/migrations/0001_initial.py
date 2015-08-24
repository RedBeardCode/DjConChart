# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CalculationRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('Name', models.TextField(verbose_name='Name of the calculation rule')),
                ('version', models.CharField(max_length=7)),
            ],
        ),
        migrations.CreateModel(
            name='CharacteristicValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='CharacteristicValueDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('Description', models.TextField(verbose_name='Description of the characteristic value')),
                ('calculation_rule', models.ForeignKey(to='MeasurementManagement.CalculationRule')),
            ],
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('date', models.DateTimeField()),
            ],
        ),
        migrations.AddField(
            model_name='characteristicvalue',
            name='measurements',
            field=models.ManyToManyField(to='MeasurementManagement.Measurement'),
        ),
        migrations.AddField(
            model_name='characteristicvalue',
            name='value_type',
            field=models.ForeignKey(to='MeasurementManagement.CharacteristicValueDescription'),
        ),
    ]
