import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from MeasurementManagement.models import CharacteristicValue
from MeasurementManagement.tests.utilies import create_correct_sample_data, create_sample_characteristic_values, \
    create_plot_config, login_as_admin


@pytest.mark.django_db
def test_plot_recalc_section(admin_client, live_server, webdriver):
    create_correct_sample_data()
    create_sample_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/gt05/')
        login_as_admin(selenium)
        assert not selenium.find_elements_by_id('recalc')
        CharacteristicValue.objects.all().update(_is_valid=False)
        selenium.get(live_server + '/plot/gt05/')
        assert selenium.find_elements_by_id('recalc')
        button = selenium.find_element_by_tag_name('button')
        assert button
        button.click()
        assert WebDriverWait(selenium, 20).until_not(EC.presence_of_element_located((By.ID, 'recalc')))
    finally:
        selenium.quit()
