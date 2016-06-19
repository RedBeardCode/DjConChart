#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from selenium.webdriver.support.ui import Select

from .utilies import login_as_admin, create_correct_sample_data, \
    login_as_limited_user, create_limited_users
from ..models import CharacteristicValueDefinition


@pytest.mark.django_db
def test_create_characteristic_value_def_view(admin_client, live_server,
                                              webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_definitions = len(CharacteristicValueDefinition.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_definition/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        definition = selenium.find_element_by_id('id_description')
        definition.send_keys('test_definition')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(
            selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(CharacteristicValueDefinition.objects.all()) == \
               num_value_definitions + 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_characteristic_value_def_noname(admin_client, live_server,
                                                webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_definitions = len(CharacteristicValueDefinition.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_definition/new/')
        login_as_admin(selenium)
        definition = selenium.find_element_by_id('id_description')
        definition.send_keys('test_definition')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(
            selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + \
                                       '/characteristic_value_definition/new/'
        assert len(CharacteristicValueDefinition.objects.all()) == \
               num_value_definitions
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_characteristic_value_def_nodes(admin_client, live_server,
                                               webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_definitions = len(CharacteristicValueDefinition.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_definition/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(
            selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + \
                                       '/characteristic_value_definition/new/'
        assert len(CharacteristicValueDefinition.objects.all()) == \
               num_value_definitions
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_characteristic_value_def_norule(admin_client, live_server,
                                                webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_definitions = len(CharacteristicValueDefinition.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_definition/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        definition = selenium.find_element_by_id('id_description')
        definition.send_keys('test_definition')
        devices = Select(
            selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + \
                                       '/characteristic_value_definition/new/'
        assert len(CharacteristicValueDefinition.objects.all()) == \
               num_value_definitions
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_characteristic_value_def_nodev(admin_client, live_server,
                                               webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_definitions = len(CharacteristicValueDefinition.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_definition/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        definition = selenium.find_element_by_id('id_description')
        definition.send_keys('test_definition')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + \
                                       '/characteristic_value_definition/new/'
        assert len(CharacteristicValueDefinition.objects.all()) == \
               num_value_definitions
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_characteristic_value_def(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        title = selenium.find_element_by_css_selector('#page-wrapper h1').text
        assert title == 'List of characteristic value definitions'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 3
        all_chara_val_des = CharacteristicValueDefinition.objects.all()
        header = selenium.find_elements_by_css_selector('#page-wrapper th')
        assert len(header) == 2
        for index, field_name in enumerate(['value_name', 'description']):
            assert header[index].text == \
                   CharacteristicValueDefinition._meta.get_field_by_name(
                       # pylint: disable=W0212
                       field_name)[0].verbose_name
        for index, row in enumerate(table_rows):
            assert row.get_attribute('data-href') == \
                   '/characteristic_value_definition/{}/'.format(
                       all_chara_val_des[index].pk)
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 2
            assert columns[0].text == columns[1].text
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_characteristic_value_def_click(admin_client, live_server,
                                             webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        all_chara_val_des = CharacteristicValueDefinition.objects.all()
        for index in range(3):
            selenium.get(live_server + '/characteristic_value_definition/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            assert selenium.current_url == \
                   live_server + '/characteristic_value_definition/{}/'.format(
                       all_chara_val_des[index].pk)

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        first_value = CharacteristicValueDefinition.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/characteristic_value_definition/',
                          live_server + '/']:
            selenium.get(start_url)
            selenium.get(
                live_server + '/characteristic_value_definition/{}/'.format(
                    first_value.pk))
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        num_values = CharacteristicValueDefinition.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == 3 - index
            table_rows[0].click()
            delete_button = selenium.find_element_by_css_selector(
                '#page-wrapper a')
            delete_button.click()
            url = '/characteristic_value_definition/{}/delete/'.format(
                CharacteristicValueDefinition.objects.all().first().pk)
            assert selenium.current_url == live_server + url
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + \
                                           '/characteristic_value_definition/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDefinition.objects.all().first()
        selenium.get(
            live_server + '/characteristic_value_definition/{}/'.format(
                first_value.pk))
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDefinition.objects.all().first()
        selenium.get(
            live_server + '/characteristic_value_definition/{}/'.format(
                first_value.pk))
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDefinition.objects.all().first()
        selenium.get(
            live_server + '/characteristic_value_definition/{}/'.format(
                first_value.pk))
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDefinition.objects.all().first()
        selenium.get(
            live_server + '/characteristic_value_definition/{}/'.format(
                first_value.pk))
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/characteristic_value_definition/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_list_new_button(admin_client, live_server,
                                                  webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new characteristic value definitions'
        buttons[0].click()
        assert selenium.current_url == live_server + \
                                       '/characteristic_value_definition/new/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_characteristic_value_def_list_new_button_limit_user(live_server,
                                                             webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 0
    finally:
        selenium.quit()
