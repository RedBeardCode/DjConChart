import pytest

from .utilies import login_as_admin, create_correct_sample_data, login_as_limited_user, create_limited_users
from ..models import Product


@pytest.mark.django_db
def test_create_product_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/product/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_product_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(Product.objects.all()) == 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_product_view_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/product/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_product_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/product/new/'
        assert len(Product.objects.all()) == 0
    finally:
        selenium.close()


@pytest.mark.django_db
def test_list_product(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/product/')
        login_as_admin(selenium)
        title = selenium.find_element_by_tag_name('h1').text
        assert title == 'List of products'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 3
        all_products = Product.objects.all()
        for index, row in enumerate(table_rows):
            assert row.get_attribute('data-href') == '/product/{}/'.format(
                all_products[index].pk)
            columns = row.find_elements_by_tag_name('td')
            assert len(columns) == 1
            assert columns[0].text == all_products[index].product_name
    finally:
        selenium.close()


@pytest.mark.django_db
def test_list_product_click(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/product/')
        login_as_admin(selenium)
        all_products = Product.objects.all()
        for index in range(3):
            selenium.get(live_server + '/product/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            assert selenium.current_url == live_server + '/product/{}/'.format(
                all_products[index].pk)

    finally:
        selenium.close()


@pytest.mark.django_db
def test_product_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/product/')
        login_as_admin(selenium)
        first_value = Product.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/product/', live_server + '/']:
            selenium.get(start_url)
            selenium.get(live_server + '/product/{}/'.format(first_value.pk))
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.close()


@pytest.mark.django_db
def test_product_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/product/')
        login_as_admin(selenium)
        num_values = Product.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == 3 - index
            table_rows[0].click()
            delete_button = selenium.find_element_by_tag_name('a')
            delete_button.click()
            assert selenium.current_url == live_server + '/product/{}/delete/'.format(
                Product.objects.all().first().pk)
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/product/'
    finally:
        selenium.close()


@pytest.mark.django_db
def test_product_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = Product.objects.all().first()
        selenium.get(live_server + '/product/{}/'.format(first_value.pk))
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_product_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = Product.objects.all().first()
        selenium.get(live_server + '/product/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_product_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = Product.objects.all().first()
        selenium.get(live_server + '/product/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_product_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = Product.objects.all().first()
        selenium.get(live_server + '/product/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/product/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_product_list_new_button(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/product/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_tag_name('a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new products'
        buttons[0].click()
        assert selenium.current_url == live_server + '/product/new/'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_product_list_new_button_limit_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/product/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_tag_name('a')
        assert len(buttons) == 0
    finally:
        selenium.close()
