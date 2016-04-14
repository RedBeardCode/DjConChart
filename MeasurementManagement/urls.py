__author__ = 'farmer'

from django.conf.urls import patterns, url
from django.contrib import admin
from django.contrib.auth.decorators import login_required

from .views import NewMeasurement, NewCalculationRule, NewMeasurementTag, recalc_characteristic_values, \
    recalculate_invalid, recalculate_progress, plot_characteristic_values, NewProduct, plot_given_configuration, \
    ListCharacteristicValueDescription, DeleteCharacteristicValueDescription, \
    UpdateCharacteristicValueDescription
from .views import NewMeasurementDevice, NewCharacteristicValueDescription, NewMeasurementItemAndOrder
from .views import NewMeasurementItem, NewMeasurementOrder, NewMeasurementOrderDefinition
from .views import get_ajax_order_info, get_ajax_meas_item

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
                       url(r'^new_measurement_order/$',
                           login_required(NewMeasurementOrder.as_view()),
                           name="new_measurement_Order"),
                       url(r'^new_measurement_order_definition/$',
                           login_required(NewMeasurementOrderDefinition.as_view()),
                           name="new_measurement_order_definition"),
                       url(r'^new_measurement_device/$',
                           login_required(NewMeasurementDevice.as_view()),
                           name="new_measurement_device"),
                       url(r'^characteristic_value_description/new/$',
                           login_required(NewCharacteristicValueDescription.as_view()),
                           name="new_characteristic_value_description"),
                       url(r'^characteristic_value_description/$',
                           login_required(ListCharacteristicValueDescription.as_view()),
                           name="list_characteristic_value_description"),
                       url(r'^characteristic_value_description/(?P<pk>\d+)/$',
                           login_required(UpdateCharacteristicValueDescription.as_view()),
                           name="update_characteristic_value_description"),
                       url(r'^characteristic_value_description/(?P<pk>\d+)/delete/$',
                           login_required(DeleteCharacteristicValueDescription.as_view()),
                           name="delete_characteristic_value_description"),
                       url(r'^new_measurement_tag/$',
                           login_required(NewMeasurementTag.as_view()),
                           name="new_measurement_tag"),
                       url(r'^new_product/$',
                           login_required(NewProduct.as_view()),
                           name="new_product"),
                       url(r'^new_item_and_order/$',
                           login_required(NewMeasurementItemAndOrder.as_view()),
                           name="new_item_and_order"),
                       url(r'^recalc_characteristic_values/$',
                           login_required(recalc_characteristic_values),
                           name="recalc_characteristic_values"),
                       url(r'^plot_characteristic_values/$',
                           login_required(plot_characteristic_values),
                           name="plot_characteristic_values"),
                       url(r'^plot/(.*)/$',
                           login_required(plot_given_configuration),
                           name="plot_given_configuration"),
                       url(r'^get_order_info/$', get_ajax_order_info, name='get_order_info'),
                       url(r'^get_meas_item/$', get_ajax_meas_item, name='get_meas_item'),
                       url(r'^recalculate_invalid/$', recalculate_invalid, name='recalculate_invalid'),
                       url(r'^recalculate_progress/$', recalculate_progress, name='recalculate_progress'),

                       )
