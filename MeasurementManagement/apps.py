from django.apps import AppConfig
from django.contrib.auth.models import Group, Permission
from django.db.models.signals import post_migrate


class MeasurementManagementConfig(AppConfig):
    name = 'MeasurementManagement'

    def ready(self):
        post_migrate.connect(self._create_user_groups, sender=self)

    def _create_user_groups(self, *args, **kwargs):
        _ = Group.objects.create(name='Viewer')

        examiner = Group.objects.create(name='Examiner')
        examiner.permissions.add(Permission.objects.get(codename='add_measurement'))
        examiner.permissions.add(Permission.objects.get(codename='add_characteristicvalue'))
        examiner.save()

        manager = Group.objects.create(name='Manager')
        [manager.permissions.add(p) for p in Permission.objects.filter(codename__contains='add')]
        [manager.permissions.add(p) for p in Permission.objects.filter(codename__contains='change')]
        manager.save()

        administrators = Group.objects.create(name='Administrator')
        [administrators.permissions.add(p) for p in Permission.objects.filter(codename__contains='add')]
        [administrators.permissions.add(p) for p in Permission.objects.filter(codename__contains='change')]
        [administrators.permissions.add(p) for p in Permission.objects.filter(codename__contains='delete')]
        administrators.save()
