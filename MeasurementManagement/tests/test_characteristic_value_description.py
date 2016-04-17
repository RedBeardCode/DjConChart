import pytest
from selenium.webdriver.support.ui import Select

from .utilies import login_as_admin, create_correct_sample_data, login_as_limited_user, create_limited_users
from ..models import CharacteristicValueDescription


@pytest.mark.django_db
def test_create_characteristic_value_desc_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_description/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions + 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_description/new/')
        login_as_admin(selenium)
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/characteristic_value_description/new/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_nodes(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_description/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/characteristic_value_description/new/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_norule(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_description/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        devices = Select(selenium.find_element_by_id('id_possible_meas_devices'))
        devices.select_by_index(0)
        devices.select_by_index(1)
        devices.select_by_index(2)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/characteristic_value_description/new/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_characteristic_value_desc_nodev(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    num_value_descriptions = len(CharacteristicValueDescription.objects.all())
    try:
        selenium.get(live_server + '/characteristic_value_description/new/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_value_name')
        name.send_keys('test_name')
        description = selenium.find_element_by_id('id_description')
        description.send_keys('test_description')
        calc_rule = Select(selenium.find_element_by_id('id_calculation_rule'))
        calc_rule.select_by_index(1)
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/characteristic_value_description/new/'
        assert len(CharacteristicValueDescription.objects.all()) == num_value_descriptions
    finally:
        selenium.close()


@pytest.mark.django_db
def test_list_characteristic_value_desc(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        title = selenium.find_element_by_tag_name('h1').text
        assert title == 'List of characteristic value descriptions'
        table_rows = selenium.find_elements_by_class_name('clickable-row')
        assert len(table_rows) == 3
        all_chara_val_des = CharacteristicValueDescription.objects.all()
        for index, row in enumerate(table_rows):
            assert row.get_attribute('data-href') == '/characteristic_value_description/{}/'.format(
                all_chara_val_des[index].pk)
            columns = row.find_elements_by_tag_name('td')
            assert len(columns) == 2
            assert columns[0].text == columns[1].text
    finally:
        selenium.close()


@pytest.mark.django_db
def test_list_characteristic_value_desc_click(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        all_chara_val_des = CharacteristicValueDescription.objects.all()
        for index in range(3):
            selenium.get(live_server + '/characteristic_value_description/')
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            table_rows[index].click()
            assert selenium.current_url == live_server + '/characteristic_value_description/{}/'.format(
                all_chara_val_des[index].pk)

    finally:
        selenium.close()


@pytest.mark.django_db
def test_characteristic_value_desc_back(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        first_value = CharacteristicValueDescription.objects.all().first()
        selenium.get(live_server + '/recalc_characteristic_values/')
        for start_url in [live_server + '/characteristic_value_description/', live_server + '/']:
            selenium.get(start_url)
            selenium.get(live_server + '/characteristic_value_description/{}/'.format(first_value.pk))
            back_button = selenium.find_elements_by_class_name('btn-default')[2]
            assert back_button.text == 'Go back'
            back_button.click()
            assert selenium.current_url == start_url
    finally:
        selenium.close()


@pytest.mark.django_db
def test_characteristic_value_desc_delete(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        num_values = CharacteristicValueDescription.objects.all().count()
        for index in range(num_values):
            table_rows = selenium.find_elements_by_class_name('clickable-row')
            assert len(table_rows) == 3 - index
            table_rows[0].click()
            delete_button = selenium.find_element_by_tag_name('a')
            delete_button.click()
            assert selenium.current_url == live_server + '/characteristic_value_description/{}/delete/'.format(
                CharacteristicValueDescription.objects.all().first().pk)
            selenium.find_element_by_class_name('btn-warning').click()
            assert selenium.current_url == live_server + '/characteristic_value_description/'
    finally:
        selenium.close()


@pytest.mark.django_db
def test_characteristic_value_desc_buttons_limited_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDescription.objects.all().first()
        selenium.get(live_server + '/characteristic_value_description/{}/'.format(first_value.pk))
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_characteristic_value_desc_buttons_change_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDescription.objects.all().first()
        selenium.get(live_server + '/characteristic_value_description/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'change_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Update'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_characteristic_value_desc_buttons_del_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDescription.objects.all().first()
        selenium.get(live_server + '/characteristic_value_description/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'delete_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Delete'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_characteristic_value_desc_buttons_add_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        first_value = CharacteristicValueDescription.objects.all().first()
        selenium.get(live_server + '/characteristic_value_description/{}/'.format(first_value.pk))
        login_as_limited_user(selenium, 'add_user')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 1
        assert buttons[0].text == 'Go back'
        selenium.get(live_server + '/characteristic_value_description/new/')
        buttons = selenium.find_elements_by_class_name('btn')
        assert len(buttons) == 2
        assert buttons[0].text == 'Submit'
        assert buttons[1].text == 'Go back'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_characteristic_value_desc_list_new_button(admin_client, live_server, webdriver):
    create_correct_sample_data()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        buttons = selenium.find_elements_by_tag_name('a')
        assert len(buttons) == 1
        assert buttons[0].text == 'Add new characteristic value descriptions'
        buttons[0].click()
        assert selenium.current_url == live_server + '/characteristic_value_description/new/'
    finally:
        selenium.close()


@pytest.mark.djangodb
def test_characteristic_value_desc_list_new_button_limit_user(live_server, webdriver):
    create_correct_sample_data()
    create_limited_users()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_limited_user(selenium)
        buttons = selenium.find_elements_by_tag_name('a')
        assert len(buttons) == 0
    finally:
        selenium.close()
