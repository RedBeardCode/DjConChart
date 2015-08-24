# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MeasurementManagement', '0002_historicalcalculationrule'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='historicalcalculationrule',
            name='history_user',
        ),
        migrations.RenameField(
            model_name='calculationrule',
            old_name='Name',
            new_name='rule_name',
        ),
        migrations.AddField(
            model_name='characteristicvaluedescription',
            name='Name of the characterisitc value',
            field=models.TextField(default='', verbose_name='Name of the characterisitc value'),
            preserve_default=False,
        ),
        migrations.DeleteModel(
            name='HistoricalCalculationRule',
        ),
    ]
