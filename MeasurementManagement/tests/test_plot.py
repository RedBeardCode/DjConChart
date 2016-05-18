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
        assert not selenium.find_elements_by_id('recalc_0')
        CharacteristicValue.objects.all().update(_is_valid=False)
        selenium.get(live_server + '/plot/gt05/')
        assert selenium.find_elements_by_id('recalc_0')
        button = selenium.find_element_by_id('recalc_values')
        assert button
        button.click()
        assert WebDriverWait(selenium, 20).until_not(EC.presence_of_element_located((By.ID, 'recalc_0')))
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_multi(admin_client, live_server, webdriver):
    create_correct_sample_data()
    create_sample_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/multi/')
        login_as_admin(selenium)
        assert len(selenium.find_elements_by_class_name('bokeh-container')) == 2
        CharacteristicValue.objects.all().update(_is_valid=False)
        selenium.get(live_server + '/plot/multi/')
        assert selenium.find_elements_by_id('recalc_0')
        assert selenium.find_elements_by_id('recalc_1')
        button = selenium.find_element_by_css_selector('#recalc_0 button')
        assert button
        button.click()
        assert WebDriverWait(selenium, 20).until_not(EC.presence_of_element_located((By.ID, 'recalc_0')))
        assert selenium.find_elements_by_id('recalc_1')
        button = selenium.find_element_by_css_selector('#recalc_1 button')
        assert button
        button.click()
        assert WebDriverWait(selenium, 20).until_not(EC.presence_of_element_located((By.ID, 'recalc_1')))
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_detail_links(admin_client, live_server, webdriver):
    create_correct_sample_data()
    create_sample_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/multi/')
        login_as_admin(selenium)
        links = selenium.find_elements_by_tag_name('a')
        assert len(links) == 2
        assert links[0].get_attribute('href') == live_server + '/plot/multi/0/'
        assert links[1].get_attribute('href') == live_server + '/plot/multi/1/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_detail_view(admin_client, live_server, webdriver):
    create_correct_sample_data()
    create_sample_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/multi/0/')
        login_as_admin(selenium)
        rows = selenium.find_elements_by_tag_name('tr')
        assert len([r for r in rows if r.text not in ['', 'inspect']]) == 11  # Strange in webkit
        columns = selenium.find_elements_by_tag_name('td')
        assert len([c for c in columns if c.text not in ['', 'inspect']]) == 40
        headers = selenium.find_elements_by_tag_name('th')
        assert len([h for h in headers if h.text not in ['', 'inspect']]) == 4
        assert [h.text for h in headers] == ['Date', 'Serial', 'Examiner', 'Value']
        selenium.get(live_server + '/plot/multi/1/')
        rows = selenium.find_elements_by_tag_name('tr')
        assert len([r for r in rows if r.text not in ['', 'inspect']]) == 7
        columns = selenium.find_elements_by_tag_name('td')
        assert len([c for c in columns if c.text not in ['', 'inspect']]) == 24
        headers = selenium.find_elements_by_tag_name('th')
        assert len([h for h in headers if h.text not in ['', 'inspect']]) == 4
        assert [h.text for h in headers] == ['Date', 'Serial', 'Examiner', 'Value']
        assert [a.text for a in selenium.find_elements_by_tag_name('a')] == ['inspect']
    finally:
        selenium.quit()
