#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views for the djcon_chart project
"""
import django.contrib.auth.views as auth_views
from django.shortcuts import redirect


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


def bokeh_redirect(request, *args, **kwargs):
    """
    Redirect to bokeh server to get the bokeh session
    """
    url = 'http://localhost:5006/autoload.js?bokeh-autoload-element={0}' \
          '&bokeh-session-id={1}'.format(
        request.GET['bokeh-autoload-element'],
        request.GET['bokeh-session-id']
    )
    return redirect(url)