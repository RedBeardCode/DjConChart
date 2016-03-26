from datetime import datetime

import pytest
import reversion as revisions
from django.contrib.auth.models import User

from .utilies import login_as_admin, create_correct_sample_data
from ..models import CalculationRule, MeasurementOrder, Measurement, MeasurementTag


@pytest.mark.django_db
def test_create_rule_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_calculation_rule/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_rule_name')
        name.send_keys('test_name')
        selenium.execute_script('editor.getSession().setValue("def calculate():</br>    pass");')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(CalculationRule.objects.all()) == 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_rule_view_nocode(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_calculation_rule/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_rule_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_calculation_rule/'
        assert len(CalculationRule.objects.all()) == 0
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_rule_view_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_calculation_rule/')
        login_as_admin(selenium)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_calculation_rule/'
        assert len(CalculationRule.objects.all()) == 0
    finally:
        selenium.close()


@pytest.mark.django_db
def test_rule_changed():
    class MockRelationManager(object):
        def all(self):
            return []

    rule = CalculationRule.objects.create(rule_name='HistTest', rule_code='def calculate(meas_dict):\n    return 1.0\n')
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
    rule = CalculationRule.objects.create(rule_name='HistTest', rule_code='def calculate(measurements):\n    pass\n')
    versions = revisions.get_for_object(rule)
    assert len(versions) == 1
    rule.rule_code = ""
    versions = revisions.get_for_object(rule)
    assert len(versions) == 1
    rule.save()
    versions = revisions.get_for_object(rule)
    assert len(versions) == 2
    rule.rule_name = ""
    versions = revisions.get_for_object(rule)
    assert len(versions) == 2
    rule.save()
    versions = revisions.get_for_object(rule)
    assert len(versions) == 3


@pytest.mark.django_db
def test_rule_history_new_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_calculation_rule/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_rule_name')
        name.send_keys('test_name')
        selenium.execute_script('editor.getSession().setValue("def calculate():</br>    pass");')
        selenium.find_element_by_tag_name('form').submit()
        rule = CalculationRule.objects.get(rule_name='test_name')
        assert rule
        versions = revisions.get_for_object(rule)
        assert len(versions) == 1
        rule.rule_code = ''
        versions = revisions.get_for_object(rule)
        assert len(versions) == 1
        rule.save()
        versions = revisions.get_for_object(rule)
        assert len(versions) == 2
    finally:
        selenium.close()


@pytest.mark.django_db
def test_rule_missing_key(admin_client):
    class MockRelationManager(object):
        def __init__(self, measurements):
            self.__measurements = measurements

        def all(self):
            return self.__measurements

    create_correct_sample_data()
    calc_rule = CalculationRule.objects.get(rule_name='calc_multi_rule')
    order = MeasurementOrder.objects.filter(order_type__name='OrderDefinition3')[0]
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



