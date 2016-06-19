#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of the django admin area
"""

# pylint: disable=R0904

from django.contrib import admin

from .models import CalculationRule, MeasurementOrder, MeasurementDevice
from .models import CharacteristicValueDefinition, Product
from .models import MeasurementItem, MeasurementOrderDefinition, MeasurementTag
from .models import PlotConfig, Measurement, CharacteristicValue


class CharacteristicValueAdmin(admin.ModelAdmin):
    """
    Admin display for CharacteristicValues
    """
    list_display = ["get_value_type_name", "value"]


class CharacteristicValueDefinitionAdmin(admin.ModelAdmin):
    """
    Admin display for CharacteristicValueDefinitions
    """
    list_display = ["value_name"]


class CalculationRuleAdmin(admin.ModelAdmin):
    """
    Admin display for CalculationRules
    """
    list_display = ["rule_name"]


admin.site.register(Measurement)
admin.site.register(MeasurementOrderDefinition)
admin.site.register(MeasurementOrder)
admin.site.register(MeasurementItem)
admin.site.register(MeasurementDevice)
admin.site.register(MeasurementTag)
admin.site.register(CharacteristicValue, CharacteristicValueAdmin)
admin.site.register(CharacteristicValueDefinition,
                    CharacteristicValueDefinitionAdmin)
admin.site.register(CalculationRule, CalculationRuleAdmin)
admin.site.register(Product)
admin.site.register(PlotConfig)
