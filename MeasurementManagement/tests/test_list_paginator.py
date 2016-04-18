import pytest

from MeasurementManagement.models import CalculationRule, CharacteristicValueDescription
from MeasurementManagement.tests.utilies import create_correct_sample_data, login_as_admin


def create_many_entries():
    rule = CalculationRule.objects.all()[0]
    for i in range(4, 100):
        CharacteristicValueDescription.objects.create(value_name='cvd {}'.format(i), description='cvd {}'.format(i),
                                                      calculation_rule=rule)


@pytest.mark.django_db
def test_list_paginator(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        assert len(selenium.find_elements_by_tag_name('tr')) == 4
        assert not selenium.find_elements_by_class_name('paginator')
        create_many_entries()
        selenium.get(live_server + '/characteristic_value_description/')
        assert len(selenium.find_elements_by_tag_name('tr')) == 21
        paginator = selenium.find_elements_by_class_name('paginator')
        assert paginator
        page_button = paginator[0].find_elements_by_tag_name('li')
        assert len(page_button) == 7
        assert page_button[0].text == '«'
        assert page_button[1].text == '1'
        assert page_button[2].text == '2'
        assert page_button[3].text == '3'
        assert page_button[4].text == '4'
        assert page_button[5].text == '5'
        assert page_button[6].text == '»'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_paginator_click_num(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_many_entries()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        paginator = selenium.find_elements_by_class_name('paginator')

        page_button = paginator[0].find_elements_by_tag_name('li')
        assert page_button[1] == selenium.find_element_by_class_name('active')
        for i in range(5, 0, -1):
            page_button[i].find_element_by_tag_name('a').click()
            assert selenium.current_url == 'http://localhost:8081/characteristic_value_description/?page={}'.format(i)
            paginator = selenium.find_element_by_class_name('paginator')
            page_button = paginator.find_elements_by_tag_name('li')
            assert page_button[i] == selenium.find_element_by_class_name('active')
            if i == 5:
                assert len(selenium.find_elements_by_tag_name('tr')) == 20
            else:
                assert len(selenium.find_elements_by_tag_name('tr')) == 21
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_paginator_click_arrow(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_many_entries()
    try:
        selenium.get(live_server + '/characteristic_value_description/')
        login_as_admin(selenium)
        paginator = selenium.find_elements_by_class_name('paginator')

        page_button = paginator[0].find_elements_by_tag_name('li')
        assert page_button[0] == selenium.find_element_by_class_name('disabled')
        assert page_button[1] == selenium.find_element_by_class_name('active')
        for i in range(2, 6):
            page_button[-1].find_element_by_tag_name('a').click()
            assert selenium.current_url == 'http://localhost:8081/characteristic_value_description/?page={}'.format(i)
            paginator = selenium.find_element_by_class_name('paginator')
            page_button = paginator.find_elements_by_tag_name('li')
            assert page_button[i] == selenium.find_element_by_class_name('active')
        assert page_button[6] == selenium.find_element_by_class_name('disabled')
    finally:
        selenium.quit()
