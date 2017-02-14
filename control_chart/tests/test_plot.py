#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from conftest import SauceLab
from .utilies import create_correct_sample_data, login_as_admin
from .utilies import create_characteristic_values, create_plot_config
from ..models import CharacteristicValue


@pytest.mark.django_db
def test_plot_recalc_section(admin_client, live_server,
                             webdriver, bokeh_server):
    create_correct_sample_data()
    create_characteristic_values()
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
        assert WebDriverWait(selenium, 20).until_not(
            EC.presence_of_element_located((By.ID, 'recalc_0')))
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_multi(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/multi/')
        login_as_admin(selenium)
        assert len(selenium.find_elements_by_class_name(
            'bk-plot-wrapper')) == 4
        CharacteristicValue.objects.all().update(_is_valid=False)
        selenium.get(live_server + '/plot/multi/')
        assert selenium.find_elements_by_id('recalc_0')
        assert selenium.find_elements_by_id('recalc_1')
        button = selenium.find_element_by_css_selector('#recalc_0 button')
        assert button
        button.click()
        assert WebDriverWait(selenium, 20).until_not(
            EC.presence_of_element_located((By.ID, 'recalc_0')))
        assert selenium.find_elements_by_id('recalc_1')
        button = selenium.find_element_by_css_selector('#recalc_1 button')
        assert button
        button.click()
        assert WebDriverWait(selenium, 20).until_not(
            EC.presence_of_element_located((By.ID, 'recalc_1')))
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_detail_links(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/multi/')
        login_as_admin(selenium)
        links = selenium.find_elements_by_css_selector('.summary a')
        assert len(links) == 2
        assert links[0].get_attribute('href') == live_server + '/plot/multi/0/'
        assert links[1].get_attribute('href') == live_server + '/plot/multi/1/'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_detail_view(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/multi/0/')
        login_as_admin(selenium)
        rows = selenium.find_elements_by_css_selector('#wrapper .table tr')
        # Strange in webkit
        assert len([r for r in rows if r.text not in ['', 'inspect']]) == 11
        columns = selenium.find_elements_by_css_selector('#wrapper .table td')
        assert len([c for c in columns if c.text not in ['', 'inspect']]) == 40
        headers = selenium.find_elements_by_css_selector('#wrapper .table th')
        assert len([h for h in headers if h.text not in ['', 'inspect']]) == 4
        assert [h.text for h in headers] == ['Date', 'Serial',
                                             'Examiner', 'Value']
        selenium.get(live_server + '/plot/multi/1/')
        rows = selenium.find_elements_by_css_selector('#wrapper .table tr')
        assert len([r for r in rows if r.text not in ['', 'inspect']]) == 7
        columns = selenium.find_elements_by_css_selector('#wrapper .table td')
        assert len([c for c in columns if c.text not in ['', 'inspect']]) == 24
        headers = selenium.find_elements_by_css_selector('#wrapper .table th')
        assert len([h for h in headers if h.text not in ['', 'inspect']]) == 4
        assert [h.text for h in headers] == ['Date', 'Serial',
                                             'Examiner', 'Value']
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_summary(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/multi/')
        login_as_admin(selenium)

        for url, num_rows, num_columns in zip(['/plot/multi/',
                                               '/plot/multi/0/',
                                               '/plot/multi/1/'],
                                              [6, 3, 3],
                                              [12, 6, 6]):
            selenium.get(live_server + url)
            rows = selenium.find_elements_by_css_selector('.summary tr')
            assert len(rows) == num_rows
            columns = selenium.find_elements_by_css_selector('.summary td')
            assert len(columns) == num_columns
            for i in range(int(num_columns / 6)):
                assert columns[1 + i * num_rows].text == '1.00'
                assert columns[3 + i * num_rows].text == '0.00'
                assert columns[5 + i * num_rows].text == '0.00'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_titles(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        if isinstance(selenium, SauceLab):
            pytest.xfail('Outworld connection not support without server')
        selenium.get(live_server + '/plot/multi/')
        login_as_admin(selenium)
        titles = selenium.find_elements_by_class_name('plot_title')
        assert len(titles) == 2
        assert titles[0].text == 'length'
        assert titles[1].text == 'width'

    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_emtpy(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    try:
        if isinstance(selenium, SauceLab):
            pytest.xfail('Outworld connection not support without server')
        selenium.get(live_server + '/plot/product3/')
        login_as_admin(selenium)
        plots = selenium.find_elements_by_class_name('bk-plot-wrapper')
        assert len(plots) == 6
    finally:
        selenium.quit()
