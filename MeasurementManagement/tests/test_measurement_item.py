import pytest
from selenium import webdriver

from .utilies import login_as_admin
from ..models import MeasurementItem


@pytest.mark.django_db
def test_create_meas_item_view(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_item/')
        login_as_admin(selenium)
        sn = selenium.find_element_by_id('id_sn')
        sn.send_keys('test_sn')
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementItem.objects.all()) == 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_meas_item_view_noname(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_item/')
        login_as_admin(selenium)
        sn = selenium.find_element_by_id('id_sn')
        sn.send_keys('test_sn')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementItem.objects.all()) == 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_meas_item_view_nosn(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_item/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_measurement_item/'
        assert len(MeasurementItem.objects.all()) == 0
    finally:
        selenium.close()