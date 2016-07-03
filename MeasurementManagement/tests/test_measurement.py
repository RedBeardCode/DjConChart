#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime

import pytest
from django.conf import settings
from django.utils.dateformat import DateFormat
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .utilies import create_grouped_users
from .utilies import create_limited_users, login_as_limited_user
from .utilies import create_sample_characteristic_values, wait_for_root_page
from .utilies import login_as_admin, create_correct_sample_data
from ..models import Measurement, MeasurementOrder, CharacteristicValue


# Create your tests here.



def test_login_requierd(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/new/')
        user_name = selenium.find_element_by_id('id_username')
        assert user_name
        assert not user_name.text
        pwd = selenium.find_element_by_id('id_password')
        assert pwd
        assert not pwd.text
        user_name.send_keys('admin')
        pwd.send_keys('password')
        selenium.find_element_by_tag_name('form').submit()
        url = selenium.current_url
        assert url == live_server + '/measurement/new/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_order_choice(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    first_index = MeasurementOrder.objects.first().pk
    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_admin(selenium)
        order = Select(selenium.find_element_by_id('id_order'))

        target_names = ['---------'] + [
            'OrderDefinition{:d} {:d} for Item {:d}: {:07d},'.format(
                i % 3 + 1, i + first_index, i, i) for i in range(10)]
        order_names = [opt.text.strip() for opt in order.options]
        assert target_names == order_names
        assert order.first_selected_option.text == '---------'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_default_values(admin_client, live_server, webdriver):
    start_create_data = datetime.datetime.now()
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_admin(selenium)
        time_delta = datetime.datetime.now() - start_create_data
        date_widget = selenium.find_element_by_id('id_date_0')
        date1_widget = selenium.find_element_by_id('id_date_1')
        date_str = date_widget.get_attribute('value') + ' '
        date_str += date1_widget.get_attribute('value')
        form_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
        assert form_date - start_create_data < time_delta
        order_select = Select(selenium.find_element_by_id('id_order'))
        assert order_select.first_selected_option.text == '---------'
        order_item = selenium.find_element_by_id('id_order_items')
        assert order_item.text.strip() == 'Please select first the order'
        examiner_select = Select(selenium.find_element_by_id('id_examiner'))
        assert examiner_select.first_selected_option.text == 'admin'
        assert selenium.find_element_by_id('id_remarks').text == ''
        meas_item_select = Select(selenium.find_element_by_id('id_meas_item'))
        assert meas_item_select.first_selected_option.text.strip() == \
               'Please select first the order'
        meas_device = selenium.find_element_by_id('id_measurement_devices')
        assert meas_device.text.strip() == 'Please select first the order'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_all_elements(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    selenium.implicitly_wait(3)
    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_admin(selenium)
        assert selenium.find_element_by_id('id_date_0')
        assert selenium.find_element_by_id('calendarlink0')
        assert selenium.find_element_by_link_text('Today')
        assert selenium.find_element_by_id('id_date_1')
        assert selenium.find_element_by_id('clocklink0')
        assert selenium.find_element_by_link_text('Now')
        assert selenium.find_element_by_id('id_order')
        assert selenium.find_element_by_id('id_order_items')
        assert selenium.find_element_by_id('id_examiner')
        assert selenium.find_element_by_id('id_remarks')
        assert selenium.find_element_by_id('id_meas_item')
        assert selenium.find_element_by_id('id_measurement_devices')
        assert selenium.find_element_by_id('id_raw_data_file')
        assert selenium.find_element_by_id('id_measurement_tag')
        assert selenium.find_element_by_class_name('btn')
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_on_change_order(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_admin(selenium)
        order = Select(selenium.find_element_by_id('id_order'))
        order_items = Select(selenium.find_element_by_id('id_order_items'))
        meas_items = Select(selenium.find_element_by_id('id_meas_item'))
        meas_devices = Select(selenium.find_element_by_id(
            'id_measurement_devices'))
        target_order_items = [['length'],
                              ['length', 'width'],
                              ['length', 'width', 'height']]
        target_meas_items = ['Item {:d}: {:07d}'.format(i, i)
                             for i in range(10)]
        target_meas_devices = [
            ['Device {:d}: {:d}'.format(i, i) for i in range(1)],
            ['Device {:d}: {:d}'.format(i, i) for i in range(3)],
            ['Device {:d}: {:d}'.format(i, i) for i in range(5)]]

        for i in range(10):
            order.select_by_index(i + 1)
            WebDriverWait(selenium, 10).until_not(
                EC.text_to_be_present_in_element(
                    (By.ID, 'id_meas_item'), '---------'))
            order_items_str = [ord.text for ord in order_items.options]
            assert order_items_str == target_order_items[i % 3]
            meas_items_str = [item.text for item in meas_items.options]
            assert meas_items_str == [target_meas_items[i]]
            meas_devices_str = [dev.text for dev in meas_devices.options]
            assert meas_devices_str == target_meas_devices[i % 3]
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_reload_failed_submit(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_admin(selenium)
        order = Select(selenium.find_element_by_id('id_order'))
        order.select_by_index(1)
        order_items = Select(selenium.find_element_by_id('id_order_items'))
        order_items.select_by_index(0)
        meas_items = Select(selenium.find_element_by_id('id_meas_item'))
        meas_items.select_by_index(0)
        meas_devices = Select(selenium.find_element_by_id(
            'id_measurement_devices'))
        meas_devices.select_by_index(0)
        button = selenium.find_element_by_css_selector('#page-wrapper button')
        button.click()
        assert selenium.current_url == live_server.url + '/measurement/new/'
        WebDriverWait(selenium, 10).until_not(EC.text_to_be_present_in_element(
            (By.ID, 'id_meas_item'), '---------'))
        reload_order = Select(selenium.find_element_by_id('id_order'))
        assert reload_order.first_selected_option.text == \
               reload_order.options[1].text
        reload_order_items = Select(selenium.find_element_by_id(
            'id_order_items'))
        assert reload_order_items.first_selected_option.text == \
               reload_order_items.options[0].text
        reload_meas_items = Select(selenium.find_element_by_id('id_meas_item'))
        assert reload_meas_items.first_selected_option.text == \
               reload_meas_items.options[0].text
        reload_meas_devices = Select(selenium.find_element_by_id(
            'id_measurement_devices'))
        assert reload_meas_devices.first_selected_option.text == \
               reload_meas_devices.options[0].text
    finally:
        selenium.quit()


@pytest.fixture(params=['Administrator', 'Examiner', 'Manager'])
def username(request):
    return request.param

@pytest.mark.django_db
def test_submit(username, live_server, webdriver):  # pylint: disable=W0621
    create_correct_sample_data()
    create_grouped_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_limited_user(selenium, user=username)
        __fill_in_single_measurement(selenium)
        button = selenium.find_elements_by_css_selector('#page-wrapper button')
        button[0].click()
        wait_for_root_page(selenium)
        assert selenium.current_url == live_server.url + '/'
        assert Measurement.objects.count() == 1
        assert CharacteristicValue.objects.count() == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_update_dlg(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()

    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_admin(selenium)
        __fill_in_single_measurement(selenium)
        button = selenium.find_elements_by_css_selector('#page-wrapper button')
        dlg = selenium.find_element_by_id("dialog-text")
        assert dlg.get_attribute('style') == 'visibility: hidden;'
        button[0].click()
        wait_for_root_page(selenium)
        assert selenium.current_url == live_server.url + '/'
        assert Measurement.objects.count() == 1
        selenium.get(live_server + '/measurement/new/')
        __fill_in_single_measurement(selenium)
        button = selenium.find_elements_by_css_selector('#page-wrapper button')
        button[0].click()
        wait = WebDriverWait(selenium, 10)
        dlg = wait.until(EC.visibility_of_element_located(
            (By.ID, 'dialog-text')))
        assert dlg.get_attribute('style') == 'visibility: visible;'  # pylint: disable=E1101
        assert selenium.find_element_by_class_name('ui-dialog')
        button = selenium.find_elements_by_css_selector('.ui-dialog button')
        assert len(button) == 3
        assert button[1].text == 'Update'
        assert button[2].text == 'Edit'
        button[2].click()
        dlg = selenium.find_element_by_id("dialog-text")
        assert dlg.get_attribute('style') == 'visibility: hidden;'
        assert selenium.current_url == live_server.url + '/measurement/new/'
        button = selenium.find_elements_by_tag_name('button')
        button[1].click()
        dlg = wait.until(EC.visibility_of_element_located(
            (By.ID, 'dialog-text')))
        button = selenium.find_elements_by_css_selector('.ui-dialog button')
        button[1].click()
        button = selenium.find_elements_by_css_selector('.ui-dialog button')
        url = '/measurement/{}/'.format(Measurement.objects.all().first().pk)
        assert selenium.current_url == live_server.url + url
        assert CharacteristicValue.objects.count() == 1
    finally:
        selenium.quit()


def __fill_in_single_measurement(selenium):
    order = Select(selenium.find_element_by_id('id_order'))
    order.select_by_index(1)
    order_items = Select(selenium.find_element_by_id('id_order_items'))
    order_items.select_by_index(0)
    meas_items = Select(selenium.find_element_by_id('id_meas_item'))
    meas_items.select_by_index(0)
    meas_devices = Select(selenium.find_element_by_id('id_measurement_devices'))
    meas_devices.select_by_index(0)
    selenium.find_element_by_id('id_remarks').send_keys('Remark')
    file_name = selenium.find_element_by_id('id_raw_data_file')
    file_name.send_keys(
        '/home/farmer/Dropbox/projects/MeasMan/samples_rsc/erste_messung.txt')


@pytest.mark.django_db
def test_submit_no_remark(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/new/')
        login_as_admin(selenium)
        order = Select(selenium.find_element_by_id('id_order'))
        order.select_by_index(1)
        order_items = Select(selenium.find_element_by_id('id_order_items'))
        order_items.select_by_index(0)
        meas_items = Select(selenium.find_element_by_id('id_meas_item'))
        meas_items.select_by_index(0)
        meas_devices = Select(selenium.find_element_by_id(
            'id_measurement_devices'))
        meas_devices.select_by_index(0)
        file_name = selenium.find_element_by_id('id_raw_data_file')
        path = '/home/farmer/Dropbox/projects/MeasMan/samples_rsc'
        file = '/erste_messung.txt'
        file_name.send_keys(path + file)
        button = selenium.find_elements_by_css_selector('#page-wrapper button')
        button[0].click()
        wait_for_root_page(selenium)
        assert selenium.current_url == live_server.url + '/'
        assert len(Measurement.objects.all()) == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement(admin_client, live_server,  # pylint: disable=R0914
                          webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_sample_characteristic_values()
    try:
        selenium.get(live_server + '/measurement/')
        login_as_admin(selenium)
        title = selenium.find_element_by_css_selector('#page-wrapper h1').text
        assert title == 'List of measurements'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 19
        all_meas = Measurement.objects.all()
        header = selenium.find_elements_by_css_selector('#page-wrapper th')
        assert len(header) == 6
        for index, field_name in enumerate(['date', 'order', 'order_items',
                                            'examiner', 'meas_item',
                                            'measurement_tag']):
            field = Measurement._meta.get_field_by_name(field_name)[0]  # pylint: disable=W0212
            assert header[index].text == field.verbose_name
        for index, row in enumerate(table_rows):
            url = '/measurement/{}/'.format(all_meas[index].pk)
            assert row.get_attribute('data-href') == url
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 6
            date = DateFormat(all_meas[index].date)
            assert columns[0].text == date.format(settings.DATETIME_FORMAT)
            assert columns[1].text == str(all_meas[index].order).strip()
            items = all_meas[index].order_items.all()
            assert columns[2].text == ';'.join([str(item) for item in items])
            assert columns[3].text == all_meas[index].examiner.username
            assert columns[4].text == str(all_meas[index].meas_item)
            assert columns[5].text == str(all_meas[index].measurement_tag)
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_click(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_sample_characteristic_values()
    try:
        selenium.get(live_server + '/measurement/')
        login_as_admin(selenium)
        all_meas = Measurement.objects.all()
        for index in range(2):
            selenium.get(live_server + '/measurement/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            url = '/measurement/{}/'.format(all_meas[index].pk)
            assert selenium.current_url == live_server + url

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_sample_characteristic_values()
    try:
        selenium.get(live_server + '/measurement/')
        login_as_admin(selenium)
        first_value = Measurement.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/measurement/', live_server + '/']:
            selenium.get(start_url)
            url = '/measurement/{}/'.format(first_value.pk)
            selenium.get(live_server + url)
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            selenium.implicitly_wait(3)
            # wait for not found page
            selenium.find_element_by_css_selector('#page-wrapper h1')
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement/')
        login_as_admin(selenium)
        num_values = Measurement.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == 2 - index
            table_rows[0].click()
            delete_button = selenium.find_element_by_css_selector(
                '#page-wrapper a')
            delete_button.click()
            url = '/measurement/{}/delete/'.format(
                Measurement.objects.all().first().pk)
            assert selenium.current_url == live_server + url
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/measurement/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    create_sample_characteristic_values()
    selenium = webdriver()
    try:
        first_value = Measurement.objects.all().first()
        selenium.get(live_server + '/measurement/{}/'.format(first_value.pk))
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    create_sample_characteristic_values()
    selenium = webdriver()
    try:
        first_value = Measurement.objects.all().first()
        selenium.get(live_server + '/measurement/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    create_sample_characteristic_values()
    selenium = webdriver()
    try:
        first_value = Measurement.objects.all().first()
        selenium.get(live_server + '/measurement/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    create_sample_characteristic_values()
    selenium = webdriver()
    try:
        first_value = Measurement.objects.all().first()
        selenium.get(live_server + '/measurement/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/measurement/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_list_new_button(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new measurements'
        buttons[0].click()
        assert selenium.current_url == live_server + '/measurement/new/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_list_new_button_limit_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 0
    finally:
        selenium.quit()
