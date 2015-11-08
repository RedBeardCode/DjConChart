__author__ = 'farmer'

from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from .views import NewMeasurement, NewCalculationRule, get_ajax_order_info
from .views import NewMeasurementItem

admin.autodiscover()


urlpatterns = patterns('MeasurementManagement.views',
                       url(r'^new_measurement/$', login_required(NewMeasurement.as_view()),
						   name="new_measurement"),
                       url(r'^new_calculation_rule/$',
                           login_required(NewCalculationRule.as_view()),
                           name="new_calculation_rule"),
                       url(r'^new_measurement_item/$',
                           login_required(NewMeasurementItem.as_view()),
                           name="new_measurement_item"),
                       url(r'^get_order_info/$', get_ajax_order_info, name='get_order_info'),
                      )