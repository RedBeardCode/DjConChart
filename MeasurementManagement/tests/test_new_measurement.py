import datetime

import pytest
from selenium import webdriver

from selenium.webdriver.support.ui import Select

from MeasurementManagement.models import MeasurementOrder, MeasurementOrderDefinition, CharacteristicValueDescription
from MeasurementManagement.models import MeasurementDevice, MeasurementItem, CalculationRule



# Create your tests here.


FAKE_TIME = datetime.datetime(2020, 12, 5, 17, 5, 55)


def login_as_admin(selenium):
    username = selenium.find_element_by_id('id_username')
    pwd = selenium.find_element_by_id('id_password')
    username.send_keys('admin')
    pwd.send_keys('password')
    selenium.find_element_by_tag_name('form').submit()


def create_correct_sample_data():
    calc_rule = CalculationRule.objects.create(rule_name="dummy", rule_code='def dummy():\n    return True\n')
    devices = [MeasurementDevice.objects.create(sn=i, name=str(i)) for i in range(5)]
    length = CharacteristicValueDescription.objects.create(value_name='length', description='length',
                                                           calculation_rule=calc_rule)
    length.possible_meas_devices.add(*devices)
    width = CharacteristicValueDescription.objects.create(value_name='width', description='width',
                                                          calculation_rule=calc_rule)
    width.possible_meas_devices.add(*devices)
    height = CharacteristicValueDescription.objects.create(value_name='height', description='height',
                                                           calculation_rule=calc_rule)
    height.possible_meas_devices.add(*devices)
    order_definition = MeasurementOrderDefinition.objects.create(name="OrderDefinition")
    order_definition.charateristic_values.add(length, width, height)
    for i in range(10):
        item = MeasurementItem.objects.create(sn=i, name=str(1))
        order = MeasurementOrder.objects.create(date=FAKE_TIME + datetime.timedelta(days=i),
                                                order_type=order_definition)
        order.measurement_items.add(item)


def test_login_requierd(admin_client, live_server):
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    username = selenium.find_element_by_id('id_username')
    assert username
    assert not (username.text)
    pwd = selenium.find_element_by_id('id_password')
    assert pwd
    assert not (pwd.text)
    username.send_keys('admin')
    pwd.send_keys('password')
    selenium.find_element_by_tag_name('form').submit()
    url = selenium.current_url
    assert url == live_server + '/new_measurement/'
    selenium.close()


@pytest.mark.django_db
def test_order_choice(admin_client, live_server):
    create_correct_sample_data()

    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    login_as_admin(selenium)
    order = Select(selenium.find_element_by_id('id_order'))

    target_names = ['---------'] + ['OrderDefinition from 2020-12-{:02d} 17:05:55+00:00'.format(i + 5) for i in
                                    range(10)]
    order_names = [opt.text for opt in order.options]
    assert target_names == order_names
    assert order.first_selected_option.text == '---------'
    selenium.close()


@pytest.mark.django_db
def test_default_values(admin_client, live_server):
    start_create_data = datetime.datetime.now()
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    login_as_admin(selenium)
    time_delta = datetime.datetime.now() - start_create_data
    date_str = selenium.find_element_by_id('id_date_0').get_attribute('value') + ' ' + selenium.find_element_by_id(
        'id_date_1').get_attribute('value')
    form_date = datetime.datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
    assert form_date - start_create_data < time_delta
    assert Select(selenium.find_element_by_id('id_order')).first_selected_option.text == '---------'
    assert selenium.find_element_by_id('id_order_items').text == 'Please select first the order'
    assert Select(selenium.find_element_by_id('id_examiner')).first_selected_option.text == 'admin'
    assert selenium.find_element_by_id('id_remarks').text == ''
    assert Select(
        selenium.find_element_by_id('id_meas_item')).first_selected_option.text == 'Please select first the order'
    assert selenium.find_element_by_id('id_measurement_devices').text == 'Please select first the order'
    selenium.close()


@pytest.mark.django_db
def test_all_elements(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    login_as_admin(selenium)
    assert selenium.find_element_by_id('id_date_0')
    assert selenium.find_element_by_id('calendarlink0')
    assert selenium.find_element_by_link_text('Today')
    assert selenium.find_element_by_id('id_date_1')
    assert selenium.find_element_by_id('clocklink0')
    assert selenium.find_element_by_link_text('Now')
    assert selenium.find_element_by_id('id_order')
    assert selenium.find_element_by_id('id_order_items')
    assert selenium.find_element_by_id('id_examiner')
    assert selenium.find_element_by_id('id_remarks')
    assert selenium.find_element_by_id('id_meas_item')
    assert selenium.find_element_by_id('id_measurement_devices')
    assert selenium.find_element_by_id('id_raw_data_file')
    assert selenium.find_element_by_class_name('btn')
    selenium.close()
