import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from .utilies import login_as_admin, create_correct_sample_data


# Create your tests here.



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

    target_names = ['---------'] + ['OrderDefinition{:d} from 2020-12-{:02d} 17:05:55+00:00'.format(i % 3 + 1, i + 5)
                                    for i in
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


@pytest.mark.django_db
def test_on_change_order(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    login_as_admin(selenium)
    order = Select(selenium.find_element_by_id('id_order'))
    order_items = Select(selenium.find_element_by_id('id_order_items'))
    meas_items = Select(selenium.find_element_by_id('id_meas_item'))
    meas_devices = Select(selenium.find_element_by_id('id_measurement_devices'))
    target_order_items = [['length'], ['length', 'width'], ['length', 'width', 'height']]
    target_meas_items = ['Item {:d}: {:d}'.format(i, i) for i in range(10)]
    target_meas_devices = [['Device {:d}: {:d}'.format(i, i) for i in range(1)],
                           ['Device {:d}: {:d}'.format(i, i) for i in range(3)],
                           ['Device {:d}: {:d}'.format(i, i) for i in range(5)]]

    for i in range(10):
        order.select_by_index(i + 1)
        assert [ord.text for ord in order_items.options] == target_order_items[i % 3]
        assert [item.text for item in meas_items.options] == [target_meas_items[i]]
        assert [dev.text for dev in meas_devices.options] == target_meas_devices[i % 3]
    selenium.close()
