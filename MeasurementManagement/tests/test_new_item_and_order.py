import pytest
from selenium import webdriver
from selenium.webdriver.support.ui import Select

from .utilies import login_as_admin, create_correct_sample_data
from ..models import MeasurementOrder, MeasurementItem


@pytest.mark.django_db
def test_all_elements(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        assert selenium.find_element_by_id('id_order_type')
        assert selenium.find_element_by_id('id_sn')
        assert selenium.find_element_by_id('id_name')
        assert selenium.find_element_by_class_name('add_meas_item_btn')
    finally:
        selenium.close()


@pytest.mark.django_db
def test_add_meas_item_ui(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)

        assert len(selenium.find_elements_by_id('id_sn')) == 1
        assert len(selenium.find_elements_by_id('id_name')) == 1
        button = selenium.find_element_by_class_name('add_meas_item_btn')
        button.click()
        assert len(selenium.find_elements_by_id('id_sn')) == 2
        assert len(selenium.find_elements_by_id('id_name')) == 2
        button.click()
        assert len(selenium.find_elements_by_id('id_sn')) == 3
        assert len(selenium.find_elements_by_id('id_name')) == 3

        groups = selenium.find_elements_by_class_name('meas-item-group')
        for index, group in enumerate(groups):
            color = group.value_of_css_property('backgroundColor')
            if index % 2:
                assert 'rgba(238, 238, 238, 1)' == color
            else:
                assert 'rgba(255, 255, 255, 1)' == color

    finally:
        selenium.close()


@pytest.mark.django_db
def test_add_meas_order_one_item(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        create_correct_sample_data()
        num_orders_before = len(MeasurementOrder.objects.all())
        num_items_before = len(MeasurementItem.objects.all())
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        name = selenium.find_element_by_id('id_name')
        name.send_keys('Teddy the bear')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        sn = selenium.find_element_by_id('id_sn')
        sn.send_keys('4711')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/'
        assert len(MeasurementOrder.objects.all()) == num_orders_before + 1
        assert len(MeasurementItem.objects.all()) == num_items_before + 1
        assert MeasurementItem.objects.get(sn=4711)
    finally:
        selenium.close()


@pytest.mark.django_db
def test_add_meas_order_two_item(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        create_correct_sample_data()
        num_orders_before = len(MeasurementOrder.objects.all())
        num_items_before = len(MeasurementItem.objects.all())
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        sns = selenium.find_elements_by_id('id_sn')
        names = selenium.find_elements_by_id('id_name')
        index = 0
        for sn, name in zip(sns, names):
            name.send_keys('Teddy the bear')
            sn.send_keys(str(4712 + index))
            index += 1
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/'
        assert len(MeasurementOrder.objects.all()) == num_orders_before + 1
        assert len(MeasurementItem.objects.all()) == num_items_before + 2
        assert MeasurementItem.objects.get(sn=4712)
        assert MeasurementItem.objects.get(sn=4713)
    finally:
        selenium.close()


@pytest.mark.django_db
def test_add_meas_order_multi_fail(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        assert len(selenium.find_elements_by_class_name('has-error')) == 4
        err_msg = selenium.find_elements_by_id('error_1_id_sn')
        assert len(err_msg) == 4
        for msg in err_msg:
            assert msg.text == "This field is required."
        selenium.find_elements_by_id('id_sn')[0].send_keys('4711')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        assert len(selenium.find_elements_by_class_name('has-error')) == 3
        err_msg = selenium.find_elements_by_id('error_1_id_sn')
        assert len(err_msg) == 3
        selenium.find_elements_by_id('id_sn')[1].send_keys('4712')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        assert len(selenium.find_elements_by_class_name('has-error')) == 2
        err_msg = selenium.find_elements_by_id('error_1_id_sn')
        assert len(err_msg) == 2
        selenium.find_elements_by_id('id_sn')[2].send_keys('4713')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        assert len(selenium.find_elements_by_class_name('has-error')) == 1
        err_msg = selenium.find_elements_by_id('error_1_id_sn')
        assert len(err_msg) == 1
        selenium.find_elements_by_id('id_sn')[3].send_keys('4714')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/')

    finally:
        selenium.close()


@pytest.mark.django_db
def test_add_meas_order_duplicate_sn(admin_client, live_server):
    selenium = webdriver.Firefox()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        sns = selenium.find_elements_by_id('id_sn')
        for sn in sns:
            sn.send_keys('1')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        alert = selenium.find_elements_by_class_name('alert')
        assert len(alert) == 1
        assert alert[0].text == 'Duplicated measurement item'

    finally:
        selenium.close()
