#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from selenium.webdriver.support.ui import Select

from .utilies import create_limited_users, login_as_limited_user
from .utilies import login_as_admin, create_correct_sample_data
from ..models import MeasurementOrder, MeasurementOrderDefinition


@pytest.mark.django_db
def test_all_elements(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_order/new/')
        login_as_admin(selenium)
        assert selenium.find_element_by_id('id_order_type')
        assert selenium.find_element_by_id('id_measurement_items')
    finally:
        selenium.quit()


@pytest.mark.djangs_db
def test_create_meas_order_view(admin_client, live_server, webdriver):
    create_correct_sample_data()
    orders_before = len(MeasurementOrder.objects.all())
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_order/new/')
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
        selenium.quit()


@pytest.mark.djangs_db
def test_create_meas_order_def_view(admin_client, live_server, webdriver):
    create_correct_sample_data()
    order_defs_before = len(MeasurementOrderDefinition.objects.all())
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_order_definition/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        mitems = Select(selenium.find_element_by_id('id_characteristic_values'))
        mitems.select_by_index(0)
        mitems.select_by_index(2)
        product = Select(selenium.find_element_by_id('id_product'))
        product.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        order_defs_after = MeasurementOrderDefinition.objects.all()
        assert len(order_defs_after) == order_defs_before + 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_order(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order/')
        login_as_admin(selenium)
        title = selenium.find_element_by_css_selector('#page-wrapper h1').text
        assert title == 'List of measurement orders'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 10
        all_meas_order = MeasurementOrder.objects.all()
        header = selenium.find_elements_by_css_selector('#page-wrapper th')
        assert len(header) == 3
        for index, field_name in enumerate(['order_nr', 'order_type',
                                            'measurement_items']):
            field = MeasurementOrder._meta.get_field(field_name)
            assert header[index].text == field.verbose_name
        for index, row in enumerate(table_rows):
            url = '/measurement_order/{}/'.format(all_meas_order[index].pk)
            assert row.get_attribute('data-href') == url
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 3
            assert columns[0].text == str(all_meas_order[index].order_nr)
            assert columns[1].text == all_meas_order[index].order_type.name
            meas_items = all_meas_order[index].measurement_items.all()
            assert columns[2].text == ' ; '.join([str(mi) for mi in meas_items])
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_order_click(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order/')
        login_as_admin(selenium)
        all_meas_order = MeasurementOrder.objects.all()
        for index in range(6):
            selenium.get(live_server + '/measurement_order/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            url = '/measurement_order/{}/'.format(all_meas_order[index].pk)
            assert selenium.current_url == live_server + url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order/')
        login_as_admin(selenium)
        first_value = MeasurementOrder.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/measurement_order/',
                          live_server + '/']:
            selenium.get(start_url)
            url = '/measurement_order/{}/'.format(first_value.pk)
            selenium.get(live_server + url)
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order/')
        login_as_admin(selenium)
        num_values = MeasurementOrder.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == num_values - index
            table_rows[0].click()
            d_button = selenium.find_element_by_css_selector('#page-wrapper a')
            d_button.click()
            url = '/measurement_order/{}/delete/'.format(
                MeasurementOrder.objects.all().first().pk)
            assert selenium.current_url == live_server + url
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/measurement_order/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrder.objects.all().first()
        url = '/measurement_order/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrder.objects.all().first()
        url = '/measurement_order/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrder.objects.all().first()
        url = '/measurement_order/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrder.objects.all().first()
        url = '/measurement_order/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/measurement_order/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_list_new_button(admin_client, live_server,
                                           webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_order/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new measurement orders'
        buttons[0].click()
        assert selenium.current_url == live_server + '/new_item_and_order/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_list_new_button_limit_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_order/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 0
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_order_definition(admin_client, live_server,
                                           webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order_definition/')
        login_as_admin(selenium)
        title = selenium.find_element_by_css_selector('#page-wrapper h1').text
        assert title == 'List of measurement order definitions'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 3
        all_meas_order_defs = MeasurementOrderDefinition.objects.all()
        header = selenium.find_elements_by_css_selector('#page-wrapper th')
        assert len(header) == 3
        for index, field_name in enumerate(['name', 'characteristic_values',
                                            'product']):
            field = MeasurementOrderDefinition._meta.get_field(field_name)
            assert header[index].text == field.verbose_name
        for index, row in enumerate(table_rows):
            assert row.get_attribute('data-href') == \
                   '/measurement_order_definition/{}/'.format(
                       all_meas_order_defs[index].pk)
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 3
            row = all_meas_order_defs[index]
            assert columns[0].text == row.name
            assert columns[1].text == row.product.product_name
            cvdefs = all_meas_order_defs[index].characteristic_values.all()
            cvd_string = ' ; '.join([cvd.value_name for cvd in cvdefs])
            assert columns[2].text == cvd_string
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_order_definition_click(admin_client, live_server,
                                                 webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order_definition/')
        login_as_admin(selenium)
        all_meas_order_defs = MeasurementOrderDefinition.objects.all()
        for index in range(3):
            selenium.get(live_server + '/measurement_order_definition/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            url = '/measurement_order_definition/{}/'.format(
                all_meas_order_defs[index].pk)
            assert selenium.current_url == live_server + url

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_back(admin_client, live_server,
                                           webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order_definition/')
        login_as_admin(selenium)
        first_value = MeasurementOrderDefinition.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/measurement_order_definition/',
                          live_server + '/']:
            selenium.get(start_url)
            url = '/measurement_order_definition/{}/'.format(first_value.pk)
            selenium.get(live_server + url)
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_delete(admin_client, live_server,
                                             webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_order_definition/')
        login_as_admin(selenium)
        num_values = MeasurementOrderDefinition.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == num_values - index
            table_rows[0].click()
            d_button = selenium.find_element_by_css_selector('#page-wrapper a')
            d_button.click()
            url = '/measurement_order_definition/{}/delete/'.format(
                MeasurementOrderDefinition.objects.all().first().pk)
            assert selenium.current_url == live_server + url
            selenium.find_element_by_class_name('btn-warning').click()
            url = '/measurement_order_definition/'
            assert selenium.current_url == live_server + url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_buttons_limited_user(live_server,
                                                           webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrderDefinition.objects.all().first()
        url = '/measurement_order_definition/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_buttons_change_user(live_server,
                                                          webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrderDefinition.objects.all().first()
        url = '/measurement_order_definition/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrderDefinition.objects.all().first()
        url = '/measurement_order_definition/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementOrderDefinition.objects.all().first()
        url = '/measurement_order_definition/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/measurement_order_definition/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_list_new_button(admin_client, live_server,
                                                      webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_order_definition/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new measurement order definitions'
        buttons[0].click()
        url = '/measurement_order_definition/new/'
        assert selenium.current_url == live_server + url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_order_definition_list_new_button_limit_user(live_server,
                                                                 webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_order_definition/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 0
    finally:
        selenium.quit()
