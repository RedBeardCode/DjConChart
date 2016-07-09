#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Url-mapping for the  control_chart app
"""

from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.decorators import login_required, permission_required

from .views import DeleteCharacteristicValueDefinition
from .views import DeleteMeasurementOrderDefinition
from .views import ListCharacteristicValueDefinition
from .views import ListPlotConfig, DeletePlotConfig
from .views import NewCalculationRule, ListCalculationRule
from .views import NewCharacteristicValueDefinition
from .views import NewMeasurement, ListMeasurement
from .views import NewMeasurementDevice, ListMeasurementDevice
from .views import NewMeasurementItem, ListMeasurementItem
from .views import NewMeasurementItemAndOrder
from .views import NewMeasurementOrder, ListMeasurementOrder
from .views import NewMeasurementOrderDefinition, ListMeasurementOrderDefinition
from .views import NewMeasurementTag, ListMeasurementTag
from .views import NewProduct, ListProduct, UpdateProduct, DeleteProduct
from .views import UpdateCalculationRule, DeleteCalculationRule, Dashboard
from .views import UpdateCharacteristicValueDefinition
from .views import UpdateMeasurement, DeleteMeasurement
from .views import UpdateMeasurementDevice, DeleteMeasurementDevice
from .views import UpdateMeasurementItem, DeleteMeasurementItem
from .views import UpdateMeasurementOrder, DeleteMeasurementOrder
from .views import UpdateMeasurementOrderDefinition
from .views import UpdateMeasurementTag, DeleteMeasurementTag
from .views import get_ajax_order_info, get_ajax_meas_item
from .views import recalc_characteristic_values, recalculate_invalid
from .views import recalculate_progress, plot_given_configuration

admin.autodiscover()

urlpatterns = [

    url(r'^measurement/new/$',
        permission_required('control_chart.add_measurement')
                            (NewMeasurement.as_view()),
        name='new_measurement'),
    url(r'^measurement/$',
        login_required(ListMeasurement.as_view()),
        name='list_measurement'),
    url(r'^measurement/(?P<pk>\d+)/$',
        login_required(UpdateMeasurement.as_view()),
        name='update_measurement'),
    url(r'^new_measurement/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_measurement')
                            (DeleteMeasurement.as_view()),
        name='delete_measurement'),

    url(r'^calculation_rule/new/$',
        permission_required('control_chart.add_calculationrule')
                            (NewCalculationRule.as_view()),
        name='new_calculation_rule'),
    url(r'^calculation_rule/$',
        login_required(ListCalculationRule.as_view()),
        name='list_calculation_rule'),
    url(r'^calculation_rule/(?P<pk>\d+)/$',
        login_required(UpdateCalculationRule.as_view()),
        name='update_calculation_rule'),
    url(r'^calculation_rule/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_calculationrule')
                            (DeleteCalculationRule.as_view()),
        name='delete_calculation_rule'),

    url(r'^measurement_item/new/$',
        permission_required('control_chart.add_measurementitem')
                            (NewMeasurementItem.as_view()),
        name='new_measurement_item'),
    url(r'^measurement_item/$',
        login_required(ListMeasurementItem.as_view()),
        name='list_measurement_item'),
    url(r'^measurement_item/(?P<pk>\d+)/$',
        login_required(UpdateMeasurementItem.as_view()),
        name='update_measurement_item'),
    url(r'^measurement_item/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_measurementitem')
                            (DeleteMeasurementItem.as_view()),
        name='delete_measurement_item'),

    url(r'^measurement_order/new/$',
        permission_required('control_chart.add_measurementorder')
                            (NewMeasurementOrder.as_view()),
        name='new_measurement_order'),
    url(r'^measurement_order/$',
        login_required(ListMeasurementOrder.as_view()),
        name='list_measurement_order'),
    url(r'^measurement_order/(?P<pk>\d+)/$',
        login_required(UpdateMeasurementOrder.as_view()),
        name='update_measurement_order'),
    url(r'^measurement_order/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_measurementorder')
                            (DeleteMeasurementOrder.as_view()),
        name='delete_measurement_order'),

    url(r'^measurement_order_definition/new/$',
        permission_required('control_chart.add_measurementorderdefinition')
                            (NewMeasurementOrderDefinition.as_view()),
        name='new_measurement_order_definition'),
    url(r'^measurement_order_definition/$',
        login_required(ListMeasurementOrderDefinition.as_view()),
        name='list_measurement_order_definition'),
    url(r'^measurement_order_definition/(?P<pk>\d+)/$',
        login_required(UpdateMeasurementOrderDefinition.as_view()),
        name='update_measurement_order_definition'),
    url(r'^measurement_order_definition/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_measurementorderdefinition')
                            (DeleteMeasurementOrderDefinition.as_view()),
        name='delete_measurement_order_definition'),

    url(r'^measurement_device/new/$',
        permission_required('control_chart.add_measurementdevice')
                            (NewMeasurementDevice.as_view()),
        name='new_measurement_device'),
    url(r'^measurement_device/$',
        login_required(ListMeasurementDevice.as_view()),
        name='list_measurement_device'),
    url(r'^measurement_device/(?P<pk>\d+)/$',
        login_required(UpdateMeasurementDevice.as_view()),
        name='update_measurement_device'),
    url(r'^measurement_device/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_measurementdevice')
                            (DeleteMeasurementDevice.as_view()),
        name='delete_measurement_device'),

    url(r'^characteristic_value_definition/new/$',
        permission_required('control_chart.add_characteristicvaluedefinition')
                            (NewCharacteristicValueDefinition.as_view()),
        name='new_characteristic_value_definition'),
    url(r'^characteristic_value_definition/$',
        login_required(ListCharacteristicValueDefinition.as_view()),
        name='list_characteristic_value_definition'),
    url(r'^characteristic_value_definition/(?P<pk>\d+)/$',
        login_required(UpdateCharacteristicValueDefinition.as_view()),
        name='update_characteristic_value_definition'),
    url(r'^characteristic_value_definition/(?P<pk>\d+)/delete/$',
        permission_required(
            'control_chart.delete_characteristicvaluedefinition')
            (DeleteCharacteristicValueDefinition.as_view()),
        name='delete_characteristic_value_definition'),

    url(r'^measurement_tag/new/$',
        permission_required('control_chart.add_measurementtag')
                            (NewMeasurementTag.as_view()),
        name='new_measurement_tag'),
    url(r'^measurement_tag/$',
        login_required(ListMeasurementTag.as_view()),
        name='list_measurement_tag'),
    url(r'^measurement_tag/(?P<pk>\d+)/$',
        login_required(UpdateMeasurementTag.as_view()),
        name='update_measurement_tag'),
    url(r'^measurement_tag/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_measurementtag')
                            (DeleteMeasurementTag.as_view()),
        name='delete_measurement_tag'),

    url(r'^product/new/$',
        permission_required('control_chart.add_product')
                            (NewProduct.as_view()),
        name='new_product'),
    url(r'^product/$',
        login_required(ListProduct.as_view()),
        name='list_product'),
    url(r'^product/(?P<pk>\d+)/$',
        login_required(UpdateProduct.as_view()),
        name='update_product'),
    url(r'^product/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.delete_product')
                            (DeleteProduct.as_view()),
        name='delete_product'),

    url(r'^plot_configuration/$',
        login_required(ListPlotConfig.as_view()),
        name='list_plot_configuration'),
    url(r'^plot_configuration/(?P<pk>\d+)/delete/$',
        permission_required('control_chart.add_plotconfiguration')
                            (DeletePlotConfig.as_view()),
        name='delete_plot_configuration'),

    # Diverse Views
    url(r'^new_item_and_order/$',
        permission_required('control_chart.add_measurementitem')
                            (NewMeasurementItemAndOrder.as_view()),
        name='new_item_and_order'),
    url(r'^recalc_characteristic_values/$',
        login_required(recalc_characteristic_values),
        name='recalc_characteristic_values'),
    url(r'^plot/(?P<configuration>[a-zA-Z0-9_.-]+)/$',
        login_required(plot_given_configuration),
        name='plot_given_configuration'),
    url(r'^plot/(?P<configuration>[a-zA-Z0-9_.-]+)/(?P<index>\d+)/$',
        login_required(plot_given_configuration),
        name='plot_given_configuration_detail'),
    url(r'^$',
        login_required(Dashboard.as_view()),
        name='dashboard'),

    # Ajax Views
    url(r'^get_order_info/$', get_ajax_order_info,
        name='get_order_info'),
    url(r'^get_meas_item/$', get_ajax_meas_item,
        name='get_meas_item'),
    url(r'^recalculate_invalid/$', recalculate_invalid,
        name='recalculate_invalid'),
    url(r'^recalculate_progress/$', recalculate_progress,
        name='recalculate_progress'),

]
