import pytest
from selenium import webdriver

from .utilies import login_as_admin
from ..models import MeasurementTag


@pytest.mark.django_db
def test_create_meas_tag_view(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_tag/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementTag.objects.all()) == 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_meas_tag_view_noname(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_measurement_tag/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_measurement_tag/'
        assert len(MeasurementTag.objects.all()) == 0
    finally:
        selenium.close()
