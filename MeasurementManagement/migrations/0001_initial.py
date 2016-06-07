# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CalculationRule',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('rule_name', models.TextField(verbose_name='Name of the calculation rule')),
                ('rule_code', models.TextField(verbose_name='Python code for the analysis')),
            ],
        ),
        migrations.CreateModel(
            name='CharacteristicValue',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('_is_valid', models.BooleanField(default=False)),
                ('_finished', models.BooleanField(default=False)),
                ('_calc_value', models.FloatField(blank=True, null=True)),
            ],
            options={
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='CharacteristicValueDescription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('value_name', models.CharField(verbose_name='Name of the characterisitc value', max_length=127)),
                ('description', models.TextField(verbose_name='Description of the characteristic value')),
                ('calculation_rule', models.ForeignKey(to='MeasurementManagement.CalculationRule')),
            ],
        ),
        migrations.CreateModel(
            name='Measurement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date', models.DateTimeField(verbose_name='Date of the measurement')),
                ('remarks', models.TextField(verbose_name='Remarks', blank=True)),
                ('raw_data_file', models.FileField(verbose_name='Raw data file', upload_to='')),
                ('examiner', models.ForeignKey(to=settings.AUTH_USER_MODEL, verbose_name='Examiner')),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementDevice',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Device name', max_length=127)),
                ('sn', models.CharField(verbose_name='Serial number', max_length=11)),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementItem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sn', models.CharField(verbose_name='Serial number of the measurement item', max_length=11)),
                ('name', models.CharField(verbose_name='Name of the measurement item', blank=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementOrder',
            fields=[
                ('order_nr', models.AutoField(primary_key=True, serialize=False, verbose_name='Order number')),
                ('measurement_items',
                 models.ManyToManyField(verbose_name='Measured items', to='MeasurementManagement.MeasurementItem')),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementOrderDefinition',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Name of the measurement order', max_length=127)),
                ('characteristic_values', models.ManyToManyField(verbose_name='Characterisctic values to be measured',
                                                                 to='MeasurementManagement.CharacteristicValueDescription')),
            ],
        ),
        migrations.CreateModel(
            name='MeasurementTag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(verbose_name='Tag to distingish measurements for one characteristic value',
                                          max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='PlotConfig',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('description', models.CharField(verbose_name='Description of the plotted data', max_length=100)),
                ('short_name',
                 models.URLField(verbose_name='Short name of configuration. Also used for url', unique=True)),
                ('histogram', models.BooleanField(verbose_name='Show histogram', default=True)),
                ('_titles', models.TextField(verbose_name='Title of the plots', default='')),
                ('_filter_args',
                 models.BinaryField(verbose_name='Pickle of list of dictionaries with filter lookup strings',
                                    blank=True)),
                ('_plot_args',
                 models.BinaryField(verbose_name='Pickle of List of dictionaries with plot parameter', blank=True)),
                ('_annotations', models.BinaryField(verbose_name='Plot annotations which should be shown', blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('product_name', models.CharField(max_length=30, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserPlotSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('bokeh_session_id', models.CharField(max_length=64)),
                ('index', models.IntegerField(verbose_name='Index of plot configuration', default=0)),
                ('plot_config',
                 models.ForeignKey(to='MeasurementManagement.PlotConfig', verbose_name='Plot configuration')),
            ],
        ),
        migrations.AddField(
            model_name='measurementorderdefinition',
            name='product',
            field=models.ForeignKey(to='MeasurementManagement.Product', verbose_name='Product to be measured'),
        ),
        migrations.AddField(
            model_name='measurementorder',
            name='order_type',
            field=models.ForeignKey(to='MeasurementManagement.MeasurementOrderDefinition',
                                    verbose_name='Based measurement order definition'),
        ),
        migrations.AddField(
            model_name='measurementitem',
            name='product',
            field=models.ForeignKey(to='MeasurementManagement.Product', verbose_name='Product'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='meas_item',
            field=models.ForeignKey(to='MeasurementManagement.MeasurementItem', verbose_name='Measurement item'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='measurement_devices',
            field=models.ManyToManyField(verbose_name='Used measurement devices',
                                         to='MeasurementManagement.MeasurementDevice'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='measurement_tag',
            field=models.ForeignKey(to='MeasurementManagement.MeasurementTag',
                                    verbose_name='Tag to distinguish the Measurements', blank=True, null=True),
        ),
        migrations.AddField(
            model_name='measurement',
            name='order',
            field=models.ForeignKey(to='MeasurementManagement.MeasurementOrder', verbose_name='Measurement order'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='order_items',
            field=models.ManyToManyField(verbose_name='Item of the measurement order',
                                         to='MeasurementManagement.CharacteristicValueDescription'),
        ),
        migrations.AddField(
            model_name='characteristicvaluedescription',
            name='possible_meas_devices',
            field=models.ManyToManyField(to='MeasurementManagement.MeasurementDevice'),
        ),
        migrations.AddField(
            model_name='characteristicvalue',
            name='measurements',
            field=models.ManyToManyField(to='MeasurementManagement.Measurement'),
        ),
        migrations.AddField(
            model_name='characteristicvalue',
            name='order',
            field=models.ForeignKey(to='MeasurementManagement.MeasurementOrder'),
        ),
        migrations.AddField(
            model_name='characteristicvalue',
            name='value_type',
            field=models.ForeignKey(to='MeasurementManagement.CharacteristicValueDescription'),
        ),
        migrations.AlterUniqueTogether(
            name='characteristicvalue',
            unique_together=set([('order', 'value_type')]),
        ),
    ]
