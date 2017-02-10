import pytest
from selenium.webdriver.support.select import Select

from .utilies import create_limited_users, login_as_limited_user
from .utilies import login_as_admin, create_correct_sample_data
from ..models import MeasurementItem, Product


@pytest.mark.django_db
def test_create_meas_item(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        Product.objects.create(product_name='product1')
        selenium.get(live_server + '/measurement_item/new/')
        login_as_admin(selenium)
        serial_nr = selenium.find_element_by_id('id_serial_nr')
        serial_nr.send_keys('test_serial_nr')
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
def test_create_meas_item_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        Product.objects.create(product_name='product1')
        selenium.get(live_server + '/measurement_item/new/')
        login_as_admin(selenium)
        serial_nr = selenium.find_element_by_id('id_serial_nr')
        serial_nr.send_keys('test_serial_nr')
        product = Select(selenium.find_element_by_id('id_product'))
        product.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(MeasurementItem.objects.all()) == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_create_meas_item_nosn(admin_client, live_server, webdriver):
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
def test_create_meas_item_noproduct(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        Product.objects.create(product_name='product1')
        selenium.get(live_server + '/measurement_item/new/')
        login_as_admin(selenium)
        serial_nr = selenium.find_element_by_id('id_serial_nr')
        serial_nr.send_keys('test_serial_nr')
        name = selenium.find_element_by_id('id_name')
        name.send_keys('name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/measurement_item/new/'
        assert len(MeasurementItem.objects.all()) == 0
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_meas_item(admin_client, live_server, webdriver):
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
        for index, field_name in enumerate(['serial_nr', 'name', 'product']):
            field = MeasurementItem._meta.get_field(field_name)
            assert header[index].text == field.verbose_name

        for index, row in enumerate(table_rows):
            url = '/measurement_item/{}/'.format(all_meas_items[index].pk)
            assert row.get_attribute('data-href') == url
            columns = row.find_elements_by_css_selector('#page-wrapper td')
            assert len(columns) == 3
            assert columns[0].text == all_meas_items[index].serial_nr
            assert columns[1].text == all_meas_items[index].name
            assert columns[2].text == \
                all_meas_items[index].product.product_name
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_meas_item_click(admin_client, live_server, webdriver):
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
            url = '/measurement_item/{}/'.format(all_meas_items[index].pk)
            assert selenium.current_url == live_server + url

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_meas_item_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/measurement_item/')
        login_as_admin(selenium)
        first_value = MeasurementItem.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/measurement_item/',
                          live_server + '/']:
            selenium.get(start_url)
            url = '/measurement_item/{}/'.format(first_value.pk)
            selenium.get(live_server + url)
            back_button = selenium.find_elements_by_class_name(
                'btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_meas_item_delete(admin_client, live_server, webdriver):
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
            d_button = selenium.find_element_by_css_selector('#page-wrapper a')
            d_button.click()
            url = '/measurement_item/{}/delete/'.format(
                MeasurementItem.objects.all().first().pk)
            assert selenium.current_url == live_server + url
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/measurement_item/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_meas_item_buttons_lu(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        url = '/measurement_item/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_meas_item_buttons_cu(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        url = '/measurement_item/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_meas_item_buttons_du(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        url = '/measurement_item/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_meas_item_buttons_au(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = MeasurementItem.objects.all().first()
        url = '/measurement_item/{}/'.format(first_value.pk)
        selenium.get(live_server + url)
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
def test_meas_item_list_new_button(admin_client, live_server, webdriver):
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
def test_meas_item_list_new_but_lu(live_server, webdriver):
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
