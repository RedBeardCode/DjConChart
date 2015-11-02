import pytest
from selenium import webdriver

from .utilies import login_as_admin
from ..models import CalculationRule


@pytest.mark.django_db
def test_create_rule_view(admin_client, live_server):
    selenium = webdriver.Firefox()
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
def test_create_rule_view_nocode(admin_client, live_server):
    selenium = webdriver.Firefox()
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
def test_create_rule_view_noname(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_calculation_rule/')
        login_as_admin(selenium)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_calculation_rule/'
        assert len(CalculationRule.objects.all()) == 0
    finally:
        selenium.close()


@pytest.mark.django_db
def test_rule_changed(admin_client, live_server):
    rule = CalculationRule.objects.create(rule_name='HistTest', rule_code='def calculate(measurements):\n    pass\n')
    assert rule.is_changed()
    rule.save()
    assert rule.is_changed()
    rule.calculate([''])
    assert not rule.is_changed()
    rule.save()
    assert rule.is_changed()
