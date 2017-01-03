#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Overwrites settings for the development
"""
import os
from .settings import *  # pylint: disable=W0401, W0614


SECRET_KEY = '7i*nqbk-z0@l@g_rz+)n##mah(lo_im55ophhdcywdc%n8cvue'
DEBUG = True

# Application definition

INSTALLED_APPS += (
    'debug_toolbar',
)

MIDDLEWARE_CLASSES += (
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

DEBUG_TOOLBAR_CONFIG = {'JQUERY_URL': ''}
