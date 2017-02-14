#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Definition of the django admin area
"""

# pylint: disable=R0904

from django.contrib import admin
from django.apps import apps

from .models import CalculationRule, MeasurementOrder, MeasurementDevice
from .models import CharacteristicValueDefinition, Product
from .models import MeasurementItem, MeasurementOrderDefinition, MeasurementTag
from .models import PlotConfig, Measurement, CharacteristicValue


if 'geo_tagging' in apps.app_configs:
    from django.contrib.gis.admin import OSMGeoAdmin

    class AdminWithOsm(OSMGeoAdmin):
        """
        Preconfigured ModelAdmin with OSMap
        """
        default_lon = -93
        default_lat = 27
        default_zoom = 15
        display_srid = 4326
else:
    class AdminWithOsm(admin.ModelAdmin):
        """
        Dummy class to make it easy to work without gis
        """
        pass


class CharacteristicValueAdmin(AdminWithOsm):
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


admin.site.register(Measurement, AdminWithOsm)
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
