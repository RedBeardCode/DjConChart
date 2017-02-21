#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Url mapping for the rest api
"""

from django.conf.urls import url, include
from rest_framework import routers
from .views import ProductRestView, MeasurementTagRestView
from .views import MeasurementOrderDefRestView, MeasurementDeviceRestView
from .views import MeasurementItemRestView, PlotConfigRestView
from .views import MeasurementRestView, CharacValDefRestView
from .views import CalculationRuleRestView, CharacteristicValueRestView
from .views import MeasurementOrderRestView, UserRestView

ROUTER = routers.DefaultRouter()
ROUTER.register(r'product', ProductRestView)
ROUTER.register(r'measurementtag', MeasurementTagRestView)
ROUTER.register(r'measurementorderdefinition', MeasurementOrderDefRestView)
ROUTER.register(r'measurementitem', MeasurementItemRestView)
ROUTER.register(r'measurementdevice', MeasurementDeviceRestView)
ROUTER.register(r'plotconfig', PlotConfigRestView)
ROUTER.register(r'measurement', MeasurementRestView)
ROUTER.register(r'characteristicvaluedefinition', CharacValDefRestView)
ROUTER.register(r'calculationrule', CalculationRuleRestView)
ROUTER.register(r'characteristicvalue', CharacteristicValueRestView)
ROUTER.register(r'measurementorder', MeasurementOrderRestView)
ROUTER.register(r'user', UserRestView)

urlpatterns = [
    url(r'^', include(ROUTER.urls)),
    url(r'^api_auth/', include('rest_framework.urls',
                               namespace='rest_framework'))
]
