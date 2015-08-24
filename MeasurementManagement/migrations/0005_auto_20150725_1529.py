# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('MeasurementManagement', '0004_auto_20150724_1022'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='calculationrule',
            name='version',
        ),
        migrations.AddField(
            model_name='calculationrule',
            name='rule_code',
            field=models.TextField(verbose_name='Pythoncode für die Auswertung', default=''),
            preserve_default=False,
        ),
    ]
