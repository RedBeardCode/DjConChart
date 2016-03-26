import pytest

from MeasurementManagement.models import MeasurementOrder
from .utilies import login_as_admin, create_correct_sample_data


@pytest.mark.django_db
def test_admin_start(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
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
        assert selenium.find_elements_by_link_text('Measurement tags')
        assert selenium.find_elements_by_link_text('Products')
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_calculation_rule(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/admin/MeasurementManagement/calculationrule/')
        login_as_admin(selenium)
        assert selenium.find_elements_by_link_text('calc_rule')
        assert selenium.find_elements_by_link_text('calc_multi_rule')
        tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
        assert tbody
        lines = tbody.find_elements_by_tag_name('tr')
        assert len(tbody.find_elements_by_tag_name('tr')) == 2
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_characteristic_value_descriptions(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/admin/MeasurementManagement/characteristicvaluedescription/')
        login_as_admin(selenium)
        tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
        assert tbody
        assert len(tbody.find_elements_by_tag_name('tr')) == 3
        assert tbody.find_element_by_link_text('height')
        assert tbody.find_element_by_link_text('width')
        assert tbody.find_element_by_link_text('length')
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_measurement_device(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
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
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_measurement_item(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/admin/MeasurementManagement/measurementitem/')
        login_as_admin(selenium)
        tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
        assert tbody
        assert len(tbody.find_elements_by_tag_name('tr')) == 10
        assert tbody.find_element_by_link_text('Item 9: 0000009')
        assert tbody.find_element_by_link_text('Item 8: 0000008')
        assert tbody.find_element_by_link_text('Item 7: 0000007')
        assert tbody.find_element_by_link_text('Item 6: 0000006')
        assert tbody.find_element_by_link_text('Item 5: 0000005')
        assert tbody.find_element_by_link_text('Item 4: 0000004')
        assert tbody.find_element_by_link_text('Item 3: 0000003')
        assert tbody.find_element_by_link_text('Item 2: 0000002')
        assert tbody.find_element_by_link_text('Item 1: 0000001')
        assert tbody.find_element_by_link_text('Item 0: 0000000')
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_measurement_order_definition(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/admin/MeasurementManagement/measurementorderdefinition/')
        login_as_admin(selenium)
        tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
        assert tbody
        assert len(tbody.find_elements_by_tag_name('tr')) == 3
        assert tbody.find_element_by_link_text('OrderDefinition3')
        assert tbody.find_element_by_link_text('OrderDefinition2')
        assert tbody.find_element_by_link_text('OrderDefinition1')
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_measurement_order(admin_client, live_server, webdriver):
    create_correct_sample_data()
    first_index = MeasurementOrder.objects.first().pk
    selenium = webdriver()
    try:
        selenium.get(live_server + '/admin/MeasurementManagement/measurementorder/')
        login_as_admin(selenium)
        tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
        assert tbody
        assert len(tbody.find_elements_by_tag_name('tr')) == 10
        assert tbody.find_element_by_link_text('OrderDefinition1 {} for Item 0: 0000000,'.format(first_index))
        assert tbody.find_element_by_link_text('OrderDefinition2 {} for Item 1: 0000001,'.format(first_index + 1))
        assert tbody.find_element_by_link_text('OrderDefinition3 {} for Item 2: 0000002,'.format(first_index + 2))
        assert tbody.find_element_by_link_text('OrderDefinition1 {} for Item 3: 0000003,'.format(first_index + 3))
        assert tbody.find_element_by_link_text('OrderDefinition2 {} for Item 4: 0000004,'.format(first_index + 4))
        assert tbody.find_element_by_link_text('OrderDefinition3 {} for Item 5: 0000005,'.format(first_index + 5))
        assert tbody.find_element_by_link_text('OrderDefinition1 {} for Item 6: 0000006,'.format(first_index + 6))
        assert tbody.find_element_by_link_text('OrderDefinition2 {} for Item 7: 0000007,'.format(first_index + 7))
        assert tbody.find_element_by_link_text('OrderDefinition3 {} for Item 8: 0000008,'.format(first_index + 8))
        assert tbody.find_element_by_link_text('OrderDefinition1 {} for Item 9: 0000009,'.format(first_index + 9))
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_measurement_tag(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/admin/MeasurementManagement/measurementtag/')
        login_as_admin(selenium)
        tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
        assert tbody
        assert len(tbody.find_elements_by_tag_name('tr')) == 2
        assert tbody.find_element_by_link_text('width')
        assert tbody.find_element_by_link_text('height')
    finally:
        selenium.close()


@pytest.mark.django_db
def test_admin_product(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/admin/MeasurementManagement/product/')
        login_as_admin(selenium)
        tbody = selenium.find_element_by_id('result_list').find_element_by_tag_name('tbody')
        assert tbody
        assert len(tbody.find_elements_by_tag_name('tr')) == 3
        assert tbody.find_element_by_link_text('product1')
        assert tbody.find_element_by_link_text('product2')
        assert tbody.find_element_by_link_text('product3')
    finally:
        selenium.close()
