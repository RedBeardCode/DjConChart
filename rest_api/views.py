#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serializers view for the rest api
"""
from django.contrib.auth.models import User
from rest_framework import viewsets
from rest_framework.permissions import DjangoModelPermissions

from control_chart.models import Product, MeasurementTag, PlotConfig
from control_chart.models import MeasurementItem, MeasurementDevice
from control_chart.models import CalculationRule, CharacteristicValueDefinition
from control_chart.models import CharacteristicValue, Measurement
from control_chart.models import MeasurementOrderDefinition, MeasurementOrder

from .serializers import ProductSerializer, MeasurementTagSerializer
from .serializers import MeasurementOrderDefSerializer, PlotConfigSerializer
from .serializers import MeasurementDeviceSerializer, MeasurementIemSerializer
from .serializers import CalculationRuleSerializer, CharaValDefSerializer
from .serializers import CharacteristicValueSerializer, MeasurementSerializer
from .serializers import MeasurementOrderSerializer, UserSerializer


class UserRestView(viewsets.ModelViewSet):
    """
    Rest view for the user model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = User.objects.all()
    serializer_class = UserSerializer


class CalculationRuleRestView(viewsets.ModelViewSet):
    """
    Rest view for the calculation rule model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = CalculationRule.objects.all()
    serializer_class = CalculationRuleSerializer


class CharacValDefRestView(viewsets.ModelViewSet):
    """
    Rest view for the characteristic value definition model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = CharacteristicValueDefinition.objects.all()
    serializer_class = CharaValDefSerializer


class CharacteristicValueRestView(viewsets.ModelViewSet):
    """
    Rest view for the characteristic value model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = CharacteristicValue.objects.all()
    serializer_class = CharacteristicValueSerializer


class MeasurementRestView(viewsets.ModelViewSet):
    """
    Rest view for the measurement model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = Measurement.objects.all()
    serializer_class = MeasurementSerializer


class ProductRestView(viewsets.ModelViewSet):
    """
    Rest view for the product model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class MeasurementTagRestView(viewsets.ModelViewSet):
    """
    Rest view for the measurement tag model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = MeasurementTag.objects.all()
    serializer_class = MeasurementTagSerializer


class MeasurementOrderDefRestView(viewsets.ModelViewSet):
    """
    Rest view for the measurement order definition model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = MeasurementOrderDefinition.objects.all()
    serializer_class = MeasurementOrderDefSerializer


class PlotConfigRestView(viewsets.ModelViewSet):
    """
    Rest view for the plot config model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = PlotConfig.objects.all()
    serializer_class = PlotConfigSerializer


class MeasurementItemRestView(viewsets.ModelViewSet):
    """
    Rest view for the measurement item model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = MeasurementItem.objects.all()
    serializer_class = MeasurementIemSerializer


class MeasurementDeviceRestView(viewsets.ModelViewSet):
    """
    Rest view for the measurement device model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = MeasurementDevice.objects.all()
    serializer_class = MeasurementDeviceSerializer


class MeasurementOrderRestView(viewsets.ModelViewSet):
    """
    Rest view for the measurement order model
    """
    permission_classes = (DjangoModelPermissions,)
    queryset = MeasurementOrder.objects.all()
    serializer_class = MeasurementOrderSerializer
