#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django settings for djcon_chart project.

"""

from .settings import *  # pylint: disable=W0401, W0614


INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',
    'reversion',
    'rest_framework',
    'rest_api',
    'crispy_forms',
    'geo_tagging',
    'control_chart',
    'leaflet',
)

try:
    DATABASES = {
        'default': {
            'ENGINE': 'django.contrib.gis.db.backends.postgis',
            'NAME': os.environ['DB_NAME'],
            'USER': os.environ['DB_USER'],
            'PASSWORD': os.environ['DB_PASS'],
            'HOST': os.environ['DB_SERVICE'],
            'PORT': os.environ['DB_PORT']
        }
    }
except KeyError:
    pass
