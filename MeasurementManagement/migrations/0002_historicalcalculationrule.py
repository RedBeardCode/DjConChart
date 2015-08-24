# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('MeasurementManagement', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalCalculationRule',
            fields=[
                ('id', models.IntegerField(auto_created=True, verbose_name='ID', db_index=True, blank=True)),
                ('Name', models.TextField(verbose_name='Name of the calculation rule')),
                ('version', models.CharField(max_length=7)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_type', models.CharField(max_length=1, choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')])),
                ('history_user', models.ForeignKey(null=True, related_name='+', on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'get_latest_by': 'history_date',
                'verbose_name': 'historical calculation rule',
                'ordering': ('-history_date', '-history_id'),
            },
        ),
    ]
