#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Serializers for the rest framework
"""
from django.contrib.auth.models import User
from control_chart.models import MeasurementTag, Product, MeasurementOrder
from control_chart.models import MeasurementOrderDefinition, Measurement
from control_chart.models import MeasurementDevice, MeasurementItem
from control_chart.models import CharacteristicValueDefinition, PlotConfig
from control_chart.models import CharacteristicValue, CalculationRule
from rest_framework import serializers


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class MeasurementSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Measurement
        fields = '__all__'


class CharaValDefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CharacteristicValueDefinition
        fields = '__all__'


class CharacteristicValueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CharacteristicValue
        fields = '__all__'


class CalculationRuleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CalculationRule
        fields = '__all__'


class ProductSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


class MeasurementTagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MeasurementTag
        fields = '__all__'


class MeasurementOrderDefSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MeasurementOrderDefinition
        fields = '__all__'


class MeasurementOrderSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MeasurementOrder
        fields = '__all__'


class MeasurementIemSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MeasurementItem
        fields = '__all__'


class MeasurementDeviceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = MeasurementDevice
        fields = '__all__'


class PlotConfigSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PlotConfig
        fields = '__all__'
