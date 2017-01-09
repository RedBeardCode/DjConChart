#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
WSGI config for djcon_chart project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.8/howto/deployment/wsgi/
"""

import os
from subprocess import Popen
import socket

from django.core.wsgi import get_wsgi_application

def port_free(port=5006):
    '''
    Checks if the port for the bokeh server is in use
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    return result != 0



local_hostname = socket.gethostname()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djcon_chart.settings")
os.environ.setdefault("BOKEH_LOAD_SERVER", "/bokeh")

#if port_free():
if False:
    server = Popen(['bokeh', 'serve', '--log-level=warning',
                    '--host={0}/bokeh'.format(local_hostname),
                    '--host={0}'.format(local_hostname),
                    '--host=localhost:5006',
                    '--host=127.0.0.1:5006',
                    '--host=*:5006',
                    '--host=*:8000',
                    '--host=*/bokeh',
                    '--host=*',
                    '--host=localhost:8000',
                    '--host=127.0.0.1:8000']
                   )

application = get_wsgi_application()  # pylint: disable=C0103