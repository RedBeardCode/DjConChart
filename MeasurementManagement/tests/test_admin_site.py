import pytest
from selenium import webdriver

from .utilies import login_as_admin, create_correct_sample_data


@pytest.mark.django_db
def test_admin_start(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/admin/')
    login_as_admin(selenium)
    assert selenium.find_elements_by_link_text('Calculation rules')
    assert selenium.find_elements_by_link_text('Characteristic value descriptions')
    assert selenium.find_elements_by_link_text('Characteristic values')
    assert selenium.find_elements_by_link_text('Measurement devices')
    assert selenium.find_elements_by_link_text('Measurement items')
    assert selenium.find_elements_by_link_text('Measurement order definitions')
    assert selenium.find_elements_by_link_text('Measurement orders')
    assert selenium.find_elements_by_link_text('Measurements')
    selenium.close()


@pytest.mark.django_db
def test_admin_calculation_rule(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/admin/MeasurementManagement/calculationrule/')
    login_as_admin(selenium)
    assert selenium.find_elements_by_link_text('dummy')
    tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
    assert tbody
    lines = tbody.find_elements_by_tag_name('tr')
    assert len(tbody.find_elements_by_tag_name('tr')) == 1
    selenium.close()


@pytest.mark.django_db
def test_admin_characteristic_value_descriptions(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/admin/MeasurementManagement/characteristicvaluedescription/')
    login_as_admin(selenium)
    tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
    assert tbody
    assert len(tbody.find_elements_by_tag_name('tr')) == 3
    assert tbody.find_element_by_link_text('height')
    assert tbody.find_element_by_link_text('width')
    assert tbody.find_element_by_link_text('length')
    selenium.close()


@pytest.mark.django_db
def test_admin_measurement_device(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/admin/MeasurementManagement/measurementdevice/')
    login_as_admin(selenium)
    tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
    assert tbody
    assert len(tbody.find_elements_by_tag_name('tr')) == 5
    assert tbody.find_element_by_link_text('Device 4: 4')
    assert tbody.find_element_by_link_text('Device 3: 3')
    assert tbody.find_element_by_link_text('Device 2: 2')
    assert tbody.find_element_by_link_text('Device 1: 1')
    assert tbody.find_element_by_link_text('Device 0: 0')
    selenium.close()


@pytest.mark.django_db
def test_admin_measurement_item(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/admin/MeasurementManagement/measurementitem/')
    login_as_admin(selenium)
    tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
    assert tbody
    assert len(tbody.find_elements_by_tag_name('tr')) == 10
    assert tbody.find_element_by_link_text('Item 9: 9')
    assert tbody.find_element_by_link_text('Item 8: 8')
    assert tbody.find_element_by_link_text('Item 7: 7')
    assert tbody.find_element_by_link_text('Item 6: 6')
    assert tbody.find_element_by_link_text('Item 5: 5')
    assert tbody.find_element_by_link_text('Item 4: 4')
    assert tbody.find_element_by_link_text('Item 3: 3')
    assert tbody.find_element_by_link_text('Item 2: 2')
    assert tbody.find_element_by_link_text('Item 1: 1')
    assert tbody.find_element_by_link_text('Item 0: 0')
    selenium.close()


@pytest.mark.django_db
def test_admin_measurement_order_definition(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/admin/MeasurementManagement/measurementorderdefinition/')
    login_as_admin(selenium)
    tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
    assert tbody
    assert len(tbody.find_elements_by_tag_name('tr')) == 3
    assert tbody.find_element_by_link_text('OrderDefinition3')
    assert tbody.find_element_by_link_text('OrderDefinition2')
    assert tbody.find_element_by_link_text('OrderDefinition1')
    selenium.close()


@pytest.mark.django_db
def test_admin_measurement_order(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/admin/MeasurementManagement/measurementorder/')
    login_as_admin(selenium)
    tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
    assert tbody
    assert len(tbody.find_elements_by_tag_name('tr')) == 10
    assert tbody.find_element_by_link_text('OrderDefinition1 from 2020-12-14 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition3 from 2020-12-13 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition2 from 2020-12-12 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition1 from 2020-12-11 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition3 from 2020-12-10 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition2 from 2020-12-09 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition1 from 2020-12-08 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition3 from 2020-12-07 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition2 from 2020-12-06 17:05:55+00:00')
    assert tbody.find_element_by_link_text('OrderDefinition1 from 2020-12-05 17:05:55+00:00')
    selenium.close()
