#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views for the djcon_chart project
"""
import os

from django.http import HttpResponse
try:
    from urllib.request import urlopen
except ImportError:
    from urllib2 import urlopen
import django.contrib.auth.views as auth_views


def login(request, *args, **kwargs):
    """
    Displays the login form with 'Remember Me' checkbox and handles the login
    action.
    """
    if request.method == 'POST':
        if not request.POST.get('remember', None):
            request.session.set_expiry(0)

    return auth_views.login(request, *args, template_name='login.html',
                            **kwargs)


def bokeh_redirect(request, *args, **kwargs):  # pylint: disable=W0613
    """
    Redirect to bokeh server to get the bokeh session
    """
    bokeh_url = os.environ.get('BOKEH_SERVER', 'http://localhost:5006/')
    url_parts = request.build_absolute_uri().split(request.path)
    base_url = url_parts[0]
    parameters = url_parts[1]
    url = '{0}autoload.js{1}'.format(bokeh_url, parameters)
    response = urlopen(url)
    html = response.read()
    html = html.replace(b'http://localhost:5006', bytearray(base_url, 'utf-8'))
    return HttpResponse(html)
