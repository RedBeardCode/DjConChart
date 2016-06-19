#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Views for the MeasMan project
"""
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
