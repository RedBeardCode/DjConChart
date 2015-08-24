# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MeasurementManagement', '0003_auto_20150723_1218'),
    ]

    operations = [
        migrations.RenameField(
            model_name='characteristicvaluedescription',
            old_name='Description',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='characteristicvaluedescription',
            old_name='Name of the characterisitc value',
            new_name='value_name',
        ),
    ]
