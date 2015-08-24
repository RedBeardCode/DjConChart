# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MeasurementManagement', '0006_auto_20150815_1237'),
    ]

    operations = [
        migrations.CreateModel(
            name='MeasurementDevice',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('name', models.TextField()),
                ('sn', models.CharField(max_length=11)),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementItem',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('sn', models.CharField(max_length=11)),
                ('name', models.TextField()),
            ],
        ),
        migrations.RemoveField(
            model_name='measurementorder',
            name='examiner',
        ),
        migrations.RemoveField(
            model_name='measurementorderdefinition',
            name='product',
        ),
        migrations.AddField(
            model_name='measurement',
            name='examiner',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='measurement',
            name='raw_data_file',
            field=models.FileField(upload_to='', default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='measurement',
            name='remarks',
            field=models.TextField(default=None),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='Product',
        ),
        migrations.AddField(
            model_name='measurement',
            name='meas_item',
            field=models.ForeignKey(to='MeasurementManagement.MeasurementItem', default=None),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='measurement',
            name='measurement_devices',
            field=models.ManyToManyField(to='MeasurementManagement.MeasurementDevice'),
        ),
    ]
