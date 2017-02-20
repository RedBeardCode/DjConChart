#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Testing the geo_tagging app
"""
from time import sleep

import pytest
from django.contrib.gis.geos import LineString
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

from control_chart.models import CharacteristicValue, Measurement, Product, \
    CharacteristicValueDefinition
from control_chart.models import MeasurementOrderDefinition, MeasurementTag
from control_chart.tests.utilies import create_item_order_meas


class TestGeoTagging(object):
    def test_add_fields(self):  # pylint: disable=R0201
        assert hasattr(Measurement, 'position')
        assert hasattr(Measurement, 'altitude')

        assert hasattr(CharacteristicValue, 'position')
        assert hasattr(CharacteristicValue, 'altitude')

    @pytest.mark.django_db
    def test_save_position_in_cv(self, test_data):  # pylint: disable=R0201,W0613
        order_type = MeasurementOrderDefinition.objects.get(
            name='OrderDefinition1')
        product = Product.objects.get(product_name='product1')
        meas = create_item_order_meas(order_type, product)
        cvalue = meas[0].characteristicvalue_set.first()
        assert meas[0].position == cvalue.position
        assert abs(meas[0].altitude - cvalue.altitude) < 0.1

    @pytest.mark.django_db
    def test_save_position_in_multicv(self, test_data):  # pylint: disable=R0201,W0613
        order_type = MeasurementOrderDefinition.objects.get(
            name='OrderDefinition3')
        product = Product.objects.get(product_name='product1')
        measurements = create_item_order_meas(order_type, product)
        cvalue = measurements[0].characteristicvalue_set.first()
        assert measurements[0].position == cvalue.position
        assert measurements[0].altitude == cvalue.altitude
        cvalue = measurements[1].characteristicvalue_set.first()
        assert measurements[1].position == cvalue.position
        assert measurements[1].altitude == cvalue.altitude
        cvalue = measurements[2].characteristicvalue_set.first()
        assert measurements[2].position == cvalue.position
        assert measurements[2].altitude == cvalue.altitude
        height_type = CharacteristicValueDefinition.objects.get(
            value_name='height')
        for meas in measurements:

            value_name = meas.order_items.first().value_name
            if value_name in ['width', 'height']:
                meas.measurement_tag = MeasurementTag.objects.get(
                    name=value_name)
                meas.order_items.add(height_type)
                meas.save()

        points = [measurements[1].position, measurements[2].position]
        mean_position = LineString(points).centroid
        mean_altitude = float(measurements[1].altitude +
                              measurements[2].altitude) / 2.0
        cvalue = measurements[2].characteristicvalue_set.first()
        cv_position = cvalue.position
        assert abs(mean_position.coords[0] - cv_position.coords[0]) < 0.1  # pylint: disable=E1101
        assert abs(mean_position.coords[1] - cv_position.coords[1]) < 0.1  # pylint: disable=E1101
        cv_altitude = cvalue.altitude
        assert abs(mean_altitude - float(cv_altitude)) < 0.1

    def test_show_map(self, working_instance, live_server, bokeh_server):  # pylint: disable=R0201
        sleep(1)
        working_instance.get(live_server.url + '/plot/product1/')
        wait = WebDriverWait(working_instance, 10)
        assert wait.until(
            EC.presence_of_element_located((By.CLASS_NAME,
                                            'leaflet-container')))
