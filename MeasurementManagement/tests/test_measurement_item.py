import pytest
from selenium.webdriver.support.select import Select

from .utilies import login_as_admin, create_correct_sample_data, create_limited_users, login_as_limited_user
from ..models import MeasurementItem, Product


@pytest.mark.django_db
def test_create_meas_item_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        Product.objects.create(product_name='product1')
        selenium.get(live_server + '/measurement_item/new/')
        login_as_admin(selenium)
        sn = selenium.find_element_by_id('id_sn')
        sn.send_keys('test_sn')
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        product = Select(selenium.find_element_by_id('id_product'))
        product.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementItem.objects.all()) == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_meas_item_view_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        Product.objects.create(product_name='product1')
        selenium.get(live_server + '/measurement_item/new/')
        login_as_admin(selenium)
        sn = selenium.find_element_by_id('id_sn')
        sn.send_keys('test_sn')
        product = Select(selenium.find_element_by_id('id_product'))
        product.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementItem.objects.all()) == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_meas_item_view_nosn(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_item/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/measurement_item/new/'
        assert len(MeasurementItem.objects.all()) == 0
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_meas_item_view_noproduct(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        Product.objects.create(product_name='product1')
        selenium.get(live_server + '/measurement_item/new/')
        login_as_admin(selenium)
        sn = selenium.find_element_by_id('id_sn')
        sn.send_keys('test_sn')
        name = selenium.find_element_by_id('id_name')
        name.send_keys('name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/measurement_item/new/'
        assert len(MeasurementItem.objects.all()) == 0
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_item(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_item/')
        login_as_admin(selenium)
        title = selenium.find_element_by_css_selector('#page-wrapper h1').text
        assert title == 'List of measurement items'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 10
        all_meas_items = MeasurementItem.objects.all()
        header = selenium.find_elements_by_css_selector('#page-wrapper th')
        assert len(header) == 3
        for index, field_name in enumerate(['sn', 'name', 'product']):
            assert header[index].text == MeasurementItem._meta.get_field_by_name(field_name)[0].verbose_name

        for index, row in enumerate(table_rows):
            assert row.get_attribute('data-href') == '/measurement_item/{}/'.format(
                all_meas_items[index].pk)
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 3
            assert columns[0].text == all_meas_items[index].sn
            assert columns[1].text == all_meas_items[index].name
            assert columns[2].text == all_meas_items[index].product.product_name
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_measurement_item_click(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_item/')
        login_as_admin(selenium)
        all_meas_items = MeasurementItem.objects.all()
        for index in range(3):
            selenium.get(live_server + '/measurement_item/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            assert selenium.current_url == live_server + '/measurement_item/{}/'.format(
                all_meas_items[index].pk)

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_item/')
        login_as_admin(selenium)
        first_value = MeasurementItem.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/measurement_item/', live_server + '/']:
            selenium.get(start_url)
            selenium.get(live_server + '/measurement_item/{}/'.format(first_value.pk))
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_item/')
        login_as_admin(selenium)
        num_values = MeasurementItem.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == 10 - index
            table_rows[0].click()
            delete_button = selenium.find_element_by_css_selector('#page-wrapper a')
            delete_button.click()
            assert selenium.current_url == live_server + '/measurement_item/{}/delete/'.format(
                MeasurementItem.objects.all().first().pk)
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/measurement_item/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        selenium.get(live_server + '/measurement_item/{}/'.format(first_value.pk))
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        selenium.get(live_server + '/measurement_item/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        selenium.get(live_server + '/measurement_item/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        selenium.get(live_server + '/measurement_item/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/measurement_item/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_list_new_button(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_item/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new measurement items'
        buttons[0].click()
        assert selenium.current_url == live_server + '/measurement_item/new/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_measurement_item_list_new_button_limit_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/measurement_item/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_css_selector('#page-wrapper a')
        assert len(buttons) == 0
    finally:
        selenium.quit()
