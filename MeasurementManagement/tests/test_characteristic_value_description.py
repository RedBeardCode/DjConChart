import pytest
from selenium.webdriver.support.ui import Select

from .utilies import login_as_admin, create_correct_sample_data
from ..models import CharacteristicValueDescription


@pytest.mark.django_db
def test_create_characteristic_value_desc_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/new_characteristic_value_description/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions + 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/new_characteristic_value_description/')
        login_as_admin(selenium)
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_characteristic_value_description/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_nodes(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/new_characteristic_value_description/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_characteristic_value_description/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_norule(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/new_characteristic_value_description/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_characteristic_value_description/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_nodev(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/new_characteristic_value_description/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_characteristic_value_description/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()
