#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Overwrites settings for the development
"""
from .settings import *  # pylint: disable=W0401, W0614


SECRET_KEY = '7i*nqbk-z0@l@g_rz+)n##mah(lo_im55ophhdcywdc%n8cvue'
DEBUG = True

# Application definition

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': 'gis',
        'USER': 'docker',
        'PASSWORD': 'docker',
        'HOST': 'localhost',
        'PORT': 25432,
    }
}


DEBUG_TOOLBAR_CONFIG = {'JQUERY_URL': ''}

INTERNAL_IPS = ['127.0.0.1']

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
