#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WSGI config for djcon_chart project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djcon_chart.settings")

application = get_wsgi_application()  # pylint: disable=C0103
