#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Overwrites settings for the development
"""
from .settings import *  # pylint: disable=W0401, W0614


SECRET_KEY = '7i*nqbk-z0@l@g_rz+)n##mah(lo_im55ophhdcywdc%n8cvue'
DEBUG = True

# Application definition



DEBUG_TOOLBAR_CONFIG = {'JQUERY_URL': ''}

INTERNAL_IPS = ['127.0.0.1']

STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'
