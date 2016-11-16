#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from .utilies import create_limited_users, login_as_limited_user
from .utilies import login_as_admin, create_correct_sample_data
from ..models import MeasurementTag


@pytest.mark.django_db
def test_create_meas_tag_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_tag/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementTag.objects.all()) == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_meas_tag_view_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_tag/new/')
        login_as_admin(selenium)
        _ = selenium.find_element_by_id('id_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/measurement_tag/new/'
        assert len(MeasurementTag.objects.all()) == 0
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_tag(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_tag/')
        login_as_admin(selenium)
        title = selenium.find_element_by_css_selector('#page-wrapper h1').text
        assert title == 'List of measurement tags'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 2
        all_meas_tags = MeasurementTag.objects.all()
        header = selenium.find_elements_by_css_selector('#page-wrapper th')
        assert len(header) == 1
        field = MeasurementTag._meta.get_field('name')
        assert header[0].text == field.verbose_name
        for index, row in enumerate(table_rows):
            url = '/measurement_tag/{}/'.format(all_meas_tags[index].pk)
            assert row.get_attribute('data-href') == url
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 1
            assert columns[0].text == all_meas_tags[index].name
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_tag_click(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_tag/')
        login_as_admin(selenium)
        all_meas_tags = MeasurementTag.objects.all()
        for index in range(2):
            selenium.get(live_server + '/measurement_tag/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            url = '/measurement_tag/{}/'.format(all_meas_tags[index].pk)
            assert selenium.current_url == live_server + url

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_tag/')
        login_as_admin(selenium)
        first_value = MeasurementTag.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/measurement_tag/', live_server + '/']:
            selenium.get(start_url)
            url = '/measurement_tag/{}/'.format(first_value.pk)
            selenium.get(live_server + url)
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_tag/')
        login_as_admin(selenium)
        num_values = MeasurementTag.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == 2 - index
            table_rows[0].click()
            d_button = selenium.find_element_by_css_selector('#page-wrapper a')
            d_button.click()
            url = '/measurement_tag/{}/delete/'.format(
                MeasurementTag.objects.all().first().pk)
            assert selenium.current_url == live_server + url
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/measurement_tag/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementTag.objects.all().first()
        url = '/measurement_tag/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementTag.objects.all().first()
        url = '/measurement_tag/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementTag.objects.all().first()
        url = '/measurement_tag/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementTag.objects.all().first()
        url = '/measurement_tag/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/measurement_tag/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_list_new_button(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_tag/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new measurement tags'
        buttons[0].click()
        assert selenium.current_url == live_server + '/measurement_tag/new/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_tag_list_new_button_limit_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_tag/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 0
    finally:
        selenium.quit()
