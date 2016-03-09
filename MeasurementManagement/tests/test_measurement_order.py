import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from .utilies import login_as_admin, create_correct_sample_data
from ..models import MeasurementOrder, MeasurementOrderDefinition


@pytest.mark.django_db
def test_all_elements(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_order/')
        login_as_admin(selenium)
        assert selenium.find_element_by_id('id_order_type')
        assert selenium.find_element_by_id('id_measurement_items')
    finally:
        selenium.close()


@pytest.mark.djangs_db
def test_create_meas_order_view(admin_client, live_server):
    create_correct_sample_data()
    orders_before = len(MeasurementOrder.objects.all())
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        meas_items = Select(selenium.find_element_by_id('id_measurement_items'))
        meas_items.select_by_index(0)
        meas_items.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementOrder.objects.all()) == orders_before + 1
    finally:
        selenium.close()


@pytest.mark.djangs_db
def test_create_meas_order_def_view(admin_client, live_server):
    create_correct_sample_data()
    order_defs_before = len(MeasurementOrderDefinition.objects.all())
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_order_definition/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        meas_items = Select(selenium.find_element_by_id('id_characteristic_values'))
        meas_items.select_by_index(0)
        meas_items.select_by_index(2)
        product = Select(selenium.find_element_by_id('id_product'))
        product.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementOrderDefinition.objects.all()) == order_defs_before + 1
    finally:
        selenium.close()
