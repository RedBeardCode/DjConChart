#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Url-mapping for the  geo_tagging app
"""

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from .views import plot_given_configuration, create_map_data

admin.autodiscover()

urlpatterns = [

    url(r'^plot/(?P<configuration>[a-zA-Z0-9_.-]+)/$',
        login_required(plot_given_configuration),
        name='plot_given_configuration'),
    url(r'^plot/(?P<configuration>[a-zA-Z0-9_.-]+)/(?P<index>\d+)/$',
        login_required(plot_given_configuration),
        name='plot_given_configuration_detail'),
    url(r'^data.geojson$', create_map_data, name='geo_plot_data')
]
