#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Contains the configuration of the MeasurementManagement App
"""

from django.apps import AppConfig
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate


class MeasurementManagementConfig(AppConfig):
    """
    App-Configuration class to handle the automatic generation of user groups
    after the migration of the database
    """
    name = 'MeasurementManagement'

    def ready(self):
        """
        Connecting the user group generation with the post_migrate signal
        """
        post_migrate.connect(MeasurementManagementConfig._create_user_groups,
                             sender=self)

    @staticmethod
    def _create_user_groups(*args, **kwargs):  # pylint: disable=W0613
        """
        Generation of the MeasurementManagement default user groups
        """
        _ = Group.objects.create(name='Viewer')

        examiner = Group.objects.create(name='Examiner')
        examiner.permissions.add(Permission.objects.get(
            codename='add_measurement'))
        examiner.permissions.add(Permission.objects.get(
            codename='add_characteristicvalue'))
        examiner.save()

        manager = Group.objects.create(name='Manager')
        _ = [manager.permissions.add(p) for p in
             Permission.objects.filter(codename__contains='add')]
        _ = [manager.permissions.add(p) for p in
             Permission.objects.filter(codename__contains='change')]
        manager.save()

        administrators = Group.objects.create(name='Administrator')
        _ = [administrators.permissions.add(p) for p in
             Permission.objects.filter(codename__contains='add')]
        _ = [administrators.permissions.add(p) for p in
             Permission.objects.filter(codename__contains='change')]
        _ = [administrators.permissions.add(p) for p in
             Permission.objects.filter(codename__contains='delete')]
        administrators.save()
