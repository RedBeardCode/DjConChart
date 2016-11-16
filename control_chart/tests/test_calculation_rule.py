#!/usr/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import pytest
from django.contrib.auth.models import User
from reversion.models import Version

from .utilies import create_limited_users, login_as_limited_user
from .utilies import login_as_admin, create_correct_sample_data
from ..models import CalculationRule, MeasurementOrder, Measurement
from ..models import MeasurementTag


@pytest.mark.django_db
def test_create_rule_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/calculation_rule/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_rule_name')
        name.send_keys('test_name')
        selenium.execute_script(
            'editor.getSession().setValue("def calculate():</br>    pass");')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(CalculationRule.objects.all()) == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_rule_view_nocode(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/calculation_rule/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_rule_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/calculation_rule/new/'
        assert len(CalculationRule.objects.all()) == 0
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_rule_view_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/calculation_rule/new/')
        login_as_admin(selenium)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/calculation_rule/new/'
        assert len(CalculationRule.objects.all()) == 0
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_rule_changed():
    class MockRelationManager(object):  # pylint: disable=R0903
        def all(self):
            return []

    rule = CalculationRule.objects.create(
        rule_name='HistTest',
        rule_code='def calculate(meas_dict):\n    return 1.0\n')
    assert rule.is_changed()
    rule.save()
    assert rule.is_changed()
    rel_mock = MockRelationManager()
    rule.calculate(rel_mock)
    assert not rule.is_changed()
    rule.save()
    assert rule.is_changed()


@pytest.mark.django_db
def test_rule_history():
    rule = CalculationRule.objects.create(
        rule_name='HistTest',
        rule_code='def calculate(measurements):\n    pass\n')
    versions = Version.objects.get_for_object(rule)
    assert len(versions) == 1
    rule.rule_code = ""
    versions = Version.objects.get_for_object(rule)
    assert len(versions) == 1
    rule.save()
    versions = Version.objects.get_for_object(rule)
    assert len(versions) == 2
    rule.rule_name = ""
    versions = Version.objects.get_for_object(rule)
    assert len(versions) == 2
    rule.save()
    versions = Version.objects.get_for_object(rule)
    assert len(versions) == 3


@pytest.mark.django_db
def test_rule_history_new_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/calculation_rule/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_rule_name')
        name.send_keys('test_name')
        selenium.execute_script(
            'editor.getSession().setValue("def calculate():</br>    pass");')
        selenium.find_element_by_tag_name('form').submit()
        rule = CalculationRule.objects.get(rule_name='test_name')
        assert rule
        versions = Version.objects.get_for_object(rule)
        assert len(versions) == 1
        rule.rule_code = ''
        versions = Version.objects.get_for_object(rule)
        assert len(versions) == 1
        rule.save()
        versions = Version.objects.get_for_object(rule)
        assert len(versions) == 2
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_rule_missing_key(admin_client):
    class MockRelationManager(object):  # pylint: disable=R0903
        def __init__(self, measurements):
            self.__measurements = measurements

        def all(self):
            return self.__measurements

    create_correct_sample_data()
    calc_rule = CalculationRule.objects.get(rule_name='calc_multi_rule')
    order = MeasurementOrder.objects.filter(
        order_type__name='OrderDefinition3')[0]
    user = User.objects.get(username='admin')
    item = order.measurement_items.all()[0]
    m_width = Measurement.objects.create(date=datetime.now(), order=order,
                                         meas_item=item, examiner=user)
    m_width.measurement_tag = MeasurementTag.objects.get(name='width')
    m_height = Measurement.objects.create(date=datetime.now(), order=order,
                                          meas_item=item, examiner=user)
    m_height.measurement_tag = MeasurementTag.objects.get(name='height')
    calc_rule.calculate(MockRelationManager([]))
    assert 'width' in calc_rule.missing_keys
    calc_rule.calculate(MockRelationManager([m_width]))
    assert 'height' in calc_rule.missing_keys
    calc_rule.calculate(MockRelationManager([m_width, m_height]))
    assert calc_rule.missing_keys == set()


@pytest.mark.django_db
def test_list_calculation_rule(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/calculation_rule/')
        login_as_admin(selenium)
        title = selenium.find_element_by_css_selector('#page-wrapper h1').text
        assert title == 'List of calculation rules'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 2
        all_calc_rules = CalculationRule.objects.all()
        header = selenium.find_elements_by_css_selector('#page-wrapper th')
        assert len(header) == 1
        assert header[0].text == \
               CalculationRule._meta.get_field('rule_name').verbose_name

        for index, row in enumerate(table_rows):
            assert row.get_attribute('data-href') == \
                   '/calculation_rule/{}/'.format(all_calc_rules[index].pk)
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 1
            assert columns[0].text == all_calc_rules[index].rule_name
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_calculation_rule_click(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/calculation_rule/')
        login_as_admin(selenium)
        all_calc_rules = CalculationRule.objects.all()
        for index in range(2):
            selenium.get(live_server + '/calculation_rule/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            assert selenium.current_url == \
                   live_server + '/calculation_rule/{}/'.format(
                       all_calc_rules[index].pk)

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/calculation_rule/')
        login_as_admin(selenium)
        first_value = CalculationRule.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/calculation_rule/',
                          live_server + '/']:
            selenium.get(start_url)
            selenium.get(live_server + '/calculation_rule/{}/'.format(
                first_value.pk))
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/calculation_rule/')
        login_as_admin(selenium)
        num_values = CalculationRule.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == 2 - index
            table_rows[0].click()
            delete_button = selenium.find_element_by_css_selector(
                '#page-wrapper a')
            delete_button.click()
            assert selenium.current_url == \
                   live_server + '/calculation_rule/{}/delete/'.format(
                       CalculationRule.objects.all().first().pk)
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/calculation_rule/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CalculationRule.objects.all().first()
        selenium.get(live_server + '/calculation_rule/{}/'.format(
            first_value.pk))
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CalculationRule.objects.all().first()
        selenium.get(live_server + '/calculation_rule/{}/'.format(
            first_value.pk))
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CalculationRule.objects.all().first()
        selenium.get(live_server + '/calculation_rule/{}/'.format(
            first_value.pk))
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CalculationRule.objects.all().first()
        selenium.get(live_server + '/calculation_rule/{}/'.format(
            first_value.pk))
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/calculation_rule/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_list_new_button(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/calculation_rule/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new calculation rules'
        buttons[0].click()
        assert selenium.current_url == live_server + '/calculation_rule/new/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_calculation_rule_list_new_button_limit_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/calculation_rule/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 0
    finally:
        selenium.quit()
