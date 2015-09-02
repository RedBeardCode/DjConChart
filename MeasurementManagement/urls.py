__author__ = 'farmer'

from django.conf.urls import patterns, url#
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from .views import MeasurementView

admin.autodiscover()


urlpatterns = patterns('MeasurementManagement.views',
                       url(r'^new_measurement/$', login_required(MeasurementView.as_view()), name="new_measurement"),

                      )