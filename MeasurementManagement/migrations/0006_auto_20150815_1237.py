# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MeasurementManagement', '0005_auto_20150725_1529'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasurementOrder',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('date', models.DateTimeField()),
                ('examiner', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementOrderDefinition',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.TextField()),
                ('charateristic_values', models.ManyToManyField(to='MeasurementManagement.CharacteristicValueDescription')),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name='measurementorderdefinition',
            name='product',
            field=models.ForeignKey(to='MeasurementManagement.Product'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='order',
            field=models.ForeignKey(to='MeasurementManagement.MeasurementOrder', default=None),
            preserve_default=False,
        ),
    ]
