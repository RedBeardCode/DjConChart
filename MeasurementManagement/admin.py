from django.contrib import admin

from .models import CalculationRule, MeasurementOrder, MeasurementDevice
from .models import Measurement, CharacteristicValue, CharacteristicValueDescription, Product
from .models import MeasurementItem, MeasurementOrderDefinition, MeasurementTag


# Register your models here.

class CharacteristicValueAdmin(admin.ModelAdmin):
    list_display = ["get_value_type_name", "value"]

class CharacteristicValueDescriptionAdmin(admin.ModelAdmin):
    list_display = ["value_name"]


class CalculationRuleAdmin(admin.ModelAdmin):
    list_display = ["rule_name"]

admin.site.register(Measurement)
admin.site.register(MeasurementOrderDefinition)
admin.site.register(MeasurementOrder)
admin.site.register(MeasurementItem)
admin.site.register(MeasurementDevice)
admin.site.register(MeasurementTag)
admin.site.register(CharacteristicValue, CharacteristicValueAdmin)
admin.site.register(CharacteristicValueDescription, CharacteristicValueDescriptionAdmin)
admin.site.register(CalculationRule, CalculationRuleAdmin)
admin.site.register(Product)
