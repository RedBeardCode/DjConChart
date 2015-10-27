import datetime

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait

from .utilies import login_as_admin, create_correct_sample_data
from ..models import Measurement


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
        WebDriverWait(selenium, 10).until_not(EC.text_to_be_present_in_element((By.ID, 'id_meas_item'), '---------'))
        assert [ord.text for ord in order_items.options] == target_order_items[i % 3]
        assert [item.text for item in meas_items.options] == [target_meas_items[i]]
        assert [dev.text for dev in meas_devices.options] == target_meas_devices[i % 3]
    selenium.close()


@pytest.mark.django_db
def test_reload_failed_submit(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    login_as_admin(selenium)
    order = Select(selenium.find_element_by_id('id_order'))
    order.select_by_index(1)
    order_items = Select(selenium.find_element_by_id('id_order_items'))
    order_items.select_by_index(0)
    meas_items = Select(selenium.find_element_by_id('id_meas_item'))
    meas_items.select_by_index(0)
    meas_devices = Select(selenium.find_element_by_id('id_measurement_devices'))
    meas_devices.select_by_index(0)
    button = selenium.find_element_by_tag_name('button')
    button.click()
    assert selenium.current_url == live_server.url + '/new_measurement/'
    WebDriverWait(selenium, 10).until_not(EC.text_to_be_present_in_element((By.ID, 'id_meas_item'), '---------'))
    reload_order = Select(selenium.find_element_by_id('id_order'))
    assert reload_order.first_selected_option.text == reload_order.options[1].text
    reload_order_items = Select(selenium.find_element_by_id('id_order_items'))
    assert reload_order_items.first_selected_option.text == reload_order_items.options[0].text
    reload_meas_items = Select(selenium.find_element_by_id('id_meas_item'))
    assert reload_meas_items.first_selected_option.text == reload_meas_items.options[0].text
    reload_meas_devices = Select(selenium.find_element_by_id('id_measurement_devices'))
    assert reload_meas_devices.first_selected_option.text == reload_meas_devices.options[0].text
    selenium.close()


@pytest.mark.django_db
def test_submit(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    login_as_admin(selenium)
    order = Select(selenium.find_element_by_id('id_order'))
    order.select_by_index(1)
    order_items = Select(selenium.find_element_by_id('id_order_items'))
    order_items.select_by_index(0)
    meas_items = Select(selenium.find_element_by_id('id_meas_item'))
    meas_items.select_by_index(0)
    meas_devices = Select(selenium.find_element_by_id('id_measurement_devices'))
    meas_devices.select_by_index(0)
    selenium.find_element_by_id('id_remarks').send_keys('Remark')
    file_name = selenium.find_element_by_id('id_raw_data_file')
    file_name.send_keys('/home/farmer/Dropbox/projects/MeasMan/samples_rsc/erste_messung.txt')
    button = selenium.find_element_by_tag_name('button')
    button.click()
    assert selenium.current_url == live_server.url + '/'
    assert len(Measurement.objects.all()) == 1
    selenium.close()


@pytest.mark.django_db
def test_submit_no_remark(admin_client, live_server):
    create_correct_sample_data()
    selenium = webdriver.Firefox()
    selenium.get(live_server + '/new_measurement/')
    login_as_admin(selenium)
    order = Select(selenium.find_element_by_id('id_order'))
    order.select_by_index(1)
    order_items = Select(selenium.find_element_by_id('id_order_items'))
    order_items.select_by_index(0)
    meas_items = Select(selenium.find_element_by_id('id_meas_item'))
    meas_items.select_by_index(0)
    meas_devices = Select(selenium.find_element_by_id('id_measurement_devices'))
    meas_devices.select_by_index(0)
    file_name = selenium.find_element_by_id('id_raw_data_file')
    file_name.send_keys('/home/farmer/Dropbox/projects/MeasMan/samples_rsc/erste_messung.txt')
    button = selenium.find_element_by_tag_name('button')
    button.click()
    assert selenium.current_url == live_server.url + '/'
    assert len(Measurement.objects.all()) == 1
    selenium.close()
