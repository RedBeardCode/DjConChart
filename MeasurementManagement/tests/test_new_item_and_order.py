import pytest
from selenium.webdriver.support.ui import Select

from .utilies import login_as_admin, create_correct_sample_data
from ..models import MeasurementOrder, MeasurementItem


@pytest.mark.django_db
def test_all_elements(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        assert selenium.find_element_by_id('id_order_type')
        assert selenium.find_element_by_id('id_sn')
        assert selenium.find_element_by_id('id_name')
        assert selenium.find_element_by_id('id_product')
        assert selenium.find_element_by_class_name('add_meas_item_btn')
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_item_ui(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)

        assert len(selenium.find_elements_by_id('id_sn')) == 1
        assert len(selenium.find_elements_by_id('id_name')) == 1
        button = selenium.find_element_by_class_name('add_meas_item_btn')
        button.click()
        assert len(selenium.find_elements_by_id('id_sn')) == 2
        assert len(selenium.find_elements_by_id('id_name')) == 2
        assert len(selenium.find_elements_by_id('id_product')) == 2
        button.click()
        assert len(selenium.find_elements_by_id('id_sn')) == 3
        assert len(selenium.find_elements_by_id('id_name')) == 3
        assert len(selenium.find_elements_by_id('id_product')) == 3

        groups = selenium.find_elements_by_class_name('meas-item-group')
        for index, group in enumerate(groups):
            color = group.value_of_css_property('backgroundColor')
            if index % 2:
                assert 'rgba(238, 238, 238, 1)' == color
            else:
                assert 'rgba(255, 255, 255, 1)' == color

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_order_one_item(admin_client, live_server, webdriver):
    selenium = webdriver()
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
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        product = Select(selenium.find_element_by_id('id_product'))
        product.select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/'
        assert len(MeasurementOrder.objects.all()) == num_orders_before + 1
        assert len(MeasurementItem.objects.all()) == num_items_before + 1
        assert MeasurementItem.objects.get(sn=4711)
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_order_two_item(admin_client, live_server, webdriver):
    selenium = webdriver()
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
        products = selenium.find_elements_by_id('id_product')
        index = 0
        for sn, name, product, in zip(sns, names, products):
            name.send_keys('Teddy the bear')
            sn.send_keys(str(4712 + index))
            Select(product).select_by_index(index % 3 + 1)
            index += 1
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == live_server.url + '/'
        assert len(MeasurementOrder.objects.all()) == num_orders_before + 1
        assert len(MeasurementItem.objects.all()) == num_items_before + 2
        assert MeasurementItem.objects.get(sn=4712)
        assert MeasurementItem.objects.get(sn=4713)
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_add_meas_order_multi_fail(admin_client, live_server, webdriver):
    selenium = webdriver()
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
        check_err_msg(selenium, 4, 4)
        selenium.find_elements_by_id('id_sn')[0].send_keys('4711')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        check_err_msg(selenium, 3, 4)
        Select(selenium.find_elements_by_id('id_product')[0]).select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        check_err_msg(selenium, 3, 3)
        selenium.find_elements_by_id('id_sn')[1].send_keys('4712')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        check_err_msg(selenium, 2, 3)
        Select(selenium.find_elements_by_id('id_product')[1]).select_by_index(2)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        check_err_msg(selenium, 2, 2)
        selenium.find_elements_by_id('id_sn')[2].send_keys('4713')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        check_err_msg(selenium, 1, 2)
        Select(selenium.find_elements_by_id('id_product')[2]).select_by_index(3)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        check_err_msg(selenium, 1, 1)
        selenium.find_elements_by_id('id_sn')[3].send_keys('4714')
        Select(selenium.find_elements_by_id('id_product')[3]).select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/')
    finally:
        selenium.quit()


def check_err_msg(selenium, num_sn_err, num_product_err):
    assert len(selenium.find_elements_by_class_name('has-error')) == num_sn_err + num_product_err
    err_msg_sn = selenium.find_elements_by_id('error_1_id_sn')
    assert len(err_msg_sn) == num_sn_err
    for msg in err_msg_sn:
        assert msg.text == "This field is required."
    err_msg_product = selenium.find_elements_by_id('error_1_id_product')
    assert len(err_msg_product) == num_product_err
    for msg in err_msg_product:
        assert msg.text == "This field is required."


@pytest.mark.django_db
def test_add_meas_order_duplicate_sn(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        order_type = Select(selenium.find_element_by_id('id_order_type'))
        order_type.select_by_index(1)
        selenium.find_element_by_class_name('add_meas_item_btn').click()
        sns = selenium.find_elements_by_id('id_sn')
        for sn in sns:
            sn.send_keys('0000001')
        selenium.find_element_by_name('action').click()
        assert selenium.current_url == (live_server.url + '/new_item_and_order/')
        alert = selenium.find_elements_by_class_name('alert')
        assert len(alert) == 1
        assert alert[0].text == 'Duplicated measurement item'

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_single_item_type(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        sn = selenium.find_element_by_id('id_sn')
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestions')) == 1
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestion')) == 0
        sn.send_keys('0')
        selenium.implicitly_wait(1)
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestion')) == 10
        sn.send_keys('000001')
        selenium.find_element_by_id('id_name').send_keys("")
        assert selenium.find_element_by_id('id_name').get_attribute('value') == 'Item 1'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_single_item_select(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        sn = selenium.find_element_by_id('id_sn')
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestions')) == 1
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestion')) == 0
        sn.send_keys('0')
        selenium.implicitly_wait(1)
        suggestions = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(suggestions) == 10
        suggestions[3].click()
        assert selenium.find_element_by_id('id_name').get_attribute('value') == 'Item 3'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_single_item_create(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        num_items = MeasurementItem.objects.count()
        Select(selenium.find_element_by_id('id_order_type')).select_by_index(1)
        sn = selenium.find_element_by_id('id_sn')
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestions')) == 1
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestion')) == 0
        sn.send_keys('4711')
        selenium.implicitly_wait(1)
        suggestions = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(suggestions) == 0
        name = selenium.find_element_by_id('id_name')
        assert name.get_attribute('value') == ''
        name.send_keys('Wasser')
        Select(selenium.find_element_by_id('id_product')).select_by_index(1)
        selenium.find_element_by_name('action').click()
        assert MeasurementItem.objects.count() == num_items + 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_ac_multi_item_select(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        create_correct_sample_data()
        selenium.get(live_server + '/new_item_and_order/')
        login_as_admin(selenium)
        button = selenium.find_element_by_class_name('add_meas_item_btn')
        button.click()
        button.click()
        sns = selenium.find_elements_by_id('id_sn')
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestions')) == 3
        assert len(selenium.find_elements_by_class_name('autocomplete-suggestion')) == 0
        sns[0].send_keys('0')
        selenium.implicitly_wait(1)
        suggestions = selenium.find_elements_by_class_name('autocomplete-suggestion')
        assert len(suggestions) == 10
        suggestions[3].click()
        names = selenium.find_elements_by_id('id_name')
        assert names[0].get_attribute('value') == 'Item 3'
        assert names[1].get_attribute('value') == ''
        assert names[2].get_attribute('value') == ''
        sns = selenium.find_elements_by_id('id_sn')
        assert sns[0].get_attribute('value') == '0000003'
        assert sns[1].get_attribute('value') == ''
        assert sns[2].get_attribute('value') == ''
    finally:
        selenium.quit()
