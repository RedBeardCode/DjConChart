#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

from .utilies import login_as_admin, create_correct_sample_data
from .utilies import wait_for_root_page
from ..models import MeasurementOrder, MeasurementItem


@pytest.mark.django_db
def test_all_elements(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        assert selenium.find_element_by_id('id_order_type')
        assert selenium.find_element_by_id('id_serial_nr')
        assert selenium.find_element_by_id('id_name')
        assert selenium.find_element_by_id('id_product')
        assert selenium.find_element_by_class_name('add_meas_item_btn')
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_item_ui(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)

        assert len(selenium.find_elements_by_id('id_serial_nr')) == 1
        assert len(selenium.find_elements_by_id('id_name')) == 1
        button = selenium.find_element_by_class_name('add_meas_item_btn')
        button.click()
        assert len(selenium.find_elements_by_id('id_serial_nr')) == 2
        assert len(selenium.find_elements_by_id('id_name')) == 2
        assert len(selenium.find_elements_by_id('id_product')) == 2
        button.click()
        assert len(selenium.find_elements_by_id('id_serial_nr')) == 3
        assert len(selenium.find_elements_by_id('id_name')) == 3
        assert len(selenium.find_elements_by_id('id_product')) == 3

        groups = selenium.find_elements_by_class_name('meas-item-group')
        for index, group in enumerate(groups):
            color = group.value_of_css_property('backgroundColor')
            if index % 2:
                assert color == 'rgba(238, 238, 238, 1)'
            else:
                assert color == 'rgba(255, 255, 255, 1)'

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_order_one_item(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        create_correct_sample_data()
        num_orders_before = len(MeasurementOrder.objects.all())
        num_items_before = len(MeasurementItem.objects.all())
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        name = selenium.find_element_by_id('id_name')
        name.send_keys('Teddy the bear')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        serial_nr = selenium.find_element_by_id('id_serial_nr')
        serial_nr.send_keys('4711')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        product = Select(selenium.find_element_by_id('id_product'))
        product.select_by_index(1)
        selenium.find_element_by_name('action').click()
        wait_for_root_page(selenium)
        assert selenium.current_url == live_server.url + '/'
        assert len(MeasurementOrder.objects.all()) == num_orders_before + 1
        assert len(MeasurementItem.objects.all()) == num_items_before + 1
        assert MeasurementItem.objects.get(serial_nr=4711)
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_order_two_item(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        create_correct_sample_data()
        num_orders_before = len(MeasurementOrder.objects.all())
        num_items_before = len(MeasurementItem.objects.all())
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        serial_nrs = selenium.find_elements_by_id('id_serial_nr')
        names = selenium.find_elements_by_id('id_name')
        products = selenium.find_elements_by_id('id_product')
        index = 0
        for serial_nr, name, product, in zip(serial_nrs, names, products):
            name.send_keys('Teddy the bear')
            serial_nr.send_keys(str(4712 + index))
            Select(product).select_by_index(index % 3 + 1)
            index += 1
        selenium.find_element_by_name('action').click()
        wait_for_root_page(selenium)
        assert selenium.current_url == live_server.url + '/'
        assert len(MeasurementOrder.objects.all()) == num_orders_before + 1
        assert len(MeasurementItem.objects.all()) == num_items_before + 2
        assert MeasurementItem.objects.get(serial_nr=4712)
        assert MeasurementItem.objects.get(serial_nr=4713)
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_order_multi_fail(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        selenium.find_elements_by_id('id_serial_nr')[0].send_keys('4711')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        Select(selenium.find_elements_by_id('id_product')[0]).select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        selenium.find_elements_by_id('id_serial_nr')[1].send_keys('4712')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        Select(selenium.find_elements_by_id('id_product')[1]).select_by_index(2)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        selenium.find_elements_by_id('id_serial_nr')[2].send_keys('4713')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        Select(selenium.find_elements_by_id('id_product')[2]).select_by_index(3)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        selenium.find_elements_by_id('id_serial_nr')[3].send_keys('4714')
        Select(selenium.find_elements_by_id('id_product')[3]).select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/'
    finally:
        selenium.quit()


def check_err_msg(selenium, num_sn_err, num_product_err):
    assert len(selenium.find_elements_by_class_name('has-error')) == \
           num_sn_err + num_product_err
    err_msg_sn = selenium.find_elements_by_id('error_1_id_serial_nr')
    assert len(err_msg_sn) == num_sn_err
    for msg in err_msg_sn:
        assert msg.text == "This field is required."
    err_msg_product = selenium.find_elements_by_id('error_1_id_product')
    assert len(err_msg_product) == num_product_err
    for msg in err_msg_product:
        assert msg.text == "This field is required."


@pytest.mark.django_db
def test_add_meas_order_duplicate_sn(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        serial_nrs = selenium.find_elements_by_id('id_serial_nr')
        for serial_nr in serial_nrs:
            serial_nr.send_keys('0000001')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/new_item_and_order/'
        alert = selenium.find_elements_by_class_name('alert')
        assert len(alert) == 1
        assert alert[0].text == 'Duplicated measurement item'

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_single_item_type(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        serial_nr = selenium.find_element_by_id('id_serial_nr')
        suggs = selenium.find_elements_by_class_name('autocomplete-suggestions')
        assert len(suggs) == 1
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 0
        serial_nr.send_keys('0')
        selenium.implicitly_wait(1)
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 10
        serial_nr.send_keys('000001\t')
        selenium.find_element_by_id('id_name').send_keys("")
        wait = WebDriverWait(selenium, 5)
        assert wait.until(EC.text_to_be_present_in_element_value(
            (By.ID, 'id_name'), 'Item 1'))
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_single_item_select(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        serial_nr = selenium.find_element_by_id('id_serial_nr')
        suggs = selenium.find_elements_by_class_name('autocomplete-suggestions')
        assert len(suggs) == 1
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 0
        serial_nr.send_keys('0')
        selenium.implicitly_wait(1)
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 10
        sugg[3].click()
        name = selenium.find_element_by_id('id_name').get_attribute('value')
        assert name == 'Item 3'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_single_item_create(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        num_items = MeasurementItem.objects.count()
        Select(selenium.find_element_by_id('id_order_type')).select_by_index(1)
        serial_nr = selenium.find_element_by_id('id_serial_nr')
        suggs = selenium.find_elements_by_class_name('autocomplete-suggestions')
        assert len(suggs) == 1
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 0
        serial_nr.send_keys('4711')
        selenium.implicitly_wait(1)
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 0
        name = selenium.find_element_by_id('id_name')
        assert name.get_attribute('value') == ''
        name.send_keys('Wasser')
        Select(selenium.find_element_by_id('id_product')).select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert MeasurementItem.objects.count() == num_items + 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_multi_item_select(admin_client, live_server, webdriver):
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        button = selenium.find_element_by_class_name('add_meas_item_btn')
        button.click()
        button.click()
        serial_nrs = selenium.find_elements_by_id('id_serial_nr')
        suggs = selenium.find_elements_by_class_name('autocomplete-suggestions')
        assert len(suggs) == 3
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 0
        serial_nrs[0].send_keys('0')
        selenium.implicitly_wait(1)
        sugg = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(sugg) == 10
        sugg[3].click()
        names = selenium.find_elements_by_id('id_name')
        assert names[0].get_attribute('value') == 'Item 3'
        assert names[1].get_attribute('value') == ''
        assert names[2].get_attribute('value') == ''
        serial_nrs = selenium.find_elements_by_id('id_serial_nr')
        assert serial_nrs[0].get_attribute('value') == '0000003'
        assert serial_nrs[1].get_attribute('value') == ''
        assert serial_nrs[2].get_attribute('value') == ''
    finally:
        selenium.quit()
