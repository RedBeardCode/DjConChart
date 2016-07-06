#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from django.contrib.auth.models import Group


class TestGroupCreation:  # pylint: disable=R0903
    @pytest.mark.django_db
    def test_init_groups(self):
        groups = Group.objects.all()
        assert len(groups) == 4
        viewer = Group.objects.get(name='Viewer')
        assert len(viewer.permissions.all()) == 0
        examiner = Group.objects.get(name='Examiner')
        assert len(examiner.permissions.all()) == 2
        manager = Group.objects.get(name='Manager')
        assert len(manager.permissions.filter(codename__contains='delete')) == 0
        admin = Group.objects.get(name='Administrator')
        assert len(admin.permissions.all()) == 60
