import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from MeasurementManagement.models import CalculationRule
from .utilies import login_as_admin, create_correct_sample_data, create_sample_characteristic_values

CALC_RULE_CODE = '''
def calculate(meas_dict):
    return 2.0\n'''


@pytest.mark.django_db
def test_recalv_finished_div(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_sample_characteristic_values()
    try:
        selenium.get(live_server + '/recalc_characteristic_values/')
        login_as_admin(selenium)
        unfinished_section = selenium.find_element_by_id('unfinished_values')
        assert not unfinished_section.is_displayed()
        unfinished_list = selenium.find_elements_by_css_selector('#unfinished_values ul li')
        assert len(unfinished_list) == 3
        collapse_button = selenium.find_element_by_id('collapse_unfinished')
        collapse_button.click()
        section_header = WebDriverWait(selenium, 1).until(
            EC.visibility_of(selenium.find_element_by_id('unfinished_values')))
        assert section_header
    finally:
        selenium.close()


@pytest.mark.django_db
def test_recalv_invalid(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_sample_characteristic_values()
    calc_rule = CalculationRule.objects.get(rule_name='calc_rule')
    calc_rule.rule_code = CALC_RULE_CODE
    calc_rule.save()
    try:
        selenium.get(live_server + '/recalc_characteristic_values/')
        login_as_admin(selenium)
        section_header = selenium.find_element_by_id('invalid_header')
        assert selenium.find_element_by_id('progress_value').text == "0%"
        assert selenium.find_element_by_class_name('progress-bar').get_attribute('style') == 'width: 0%;'
        assert section_header.text == '16'
        recalc_button = selenium.find_element_by_id('recalc_values')
        recalc_button.click()
        selenium.implicitly_wait(3)
        section_header = WebDriverWait(selenium, 5).until(
            EC.text_to_be_present_in_element((By.ID, 'invalid_header'), '0/16'))
        assert section_header
        assert selenium.find_element_by_id('progress_value').text == '100%'
        assert selenium.find_element_by_class_name('progress-bar').get_attribute('style') == 'width: 100%;'
    finally:
        selenium.close()
