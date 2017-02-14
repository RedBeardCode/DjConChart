#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from control_chart.models import CalculationRule
from control_chart.models import CharacteristicValueDefinition
from control_chart.tests.utilies import create_correct_sample_data
from control_chart.tests.utilies import login_as_admin


def create_many_entries():
    rule = CalculationRule.objects.all()[0]
    for i in range(4, 100):
        CharacteristicValueDefinition.objects.create(
            value_name='cvd {}'.format(i),
            description='cvd {}'.format(i),
            calculation_rule=rule)


@pytest.mark.django_db
def test_list_paginator(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        rows = selenium.find_elements_by_css_selector('#page-wrapper tr')
        assert len(rows) == 4
        assert not selenium.find_elements_by_class_name('paginator')
        create_many_entries()
        selenium.get(live_server + '/characteristic_value_definition/')
        rows = selenium.find_elements_by_css_selector('#page-wrapper tr')
        assert len(rows) == 21
        paginator = selenium.find_elements_by_class_name('paginator')
        assert paginator
        button = paginator[0].find_elements_by_css_selector('#page-wrapper li')
        assert len(button) == 7
        assert button[0].text == u'«'
        assert button[1].text == '1'
        assert button[2].text == '2'
        assert button[3].text == '3'
        assert button[4].text == '4'
        assert button[5].text == '5'
        assert button[6].text == u'»'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_paginator_click_num(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_many_entries()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        paginator = selenium.find_elements_by_class_name('paginator')

        button = paginator[0].find_elements_by_css_selector('#page-wrapper li')
        assert button[1] == selenium.find_element_by_css_selector(
            '#page-wrapper .active')
        for i in range(5, 0, -1):
            button[i].find_element_by_css_selector('#page-wrapper a').click()
            url = '/characteristic_value_definition/?page={}'.format(i)
            assert selenium.current_url == live_server.url + url
            paginator = selenium.find_element_by_class_name('paginator')
            button = paginator.find_elements_by_css_selector(
                '#page-wrapper li')
            active = selenium.find_element_by_css_selector(
                '#page-wrapper .active')
            assert button[i] == active
            row = selenium.find_elements_by_css_selector('#page-wrapper tr')
            if i == 5:
                assert len(row) == 20
            else:
                assert len(row) == 21
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_list_paginator_click_arrow(admin_client, live_server, webdriver):
    selenium = webdriver()
    create_correct_sample_data()
    create_many_entries()
    try:
        selenium.get(live_server + '/characteristic_value_definition/')
        login_as_admin(selenium)
        paginator = selenium.find_elements_by_class_name('paginator')

        button = paginator[0].find_elements_by_css_selector('#page-wrapper li')
        assert button[0] == selenium.find_element_by_css_selector(
            '#page-wrapper .disabled')
        assert button[1] == selenium.find_element_by_css_selector(
            '#page-wrapper .active')
        for i in range(2, 6):
            button[-1].find_element_by_css_selector('#page-wrapper a').click()
            url = '/characteristic_value_definition/?page={}'.format(i)
            assert selenium.current_url == live_server.url + url
            paginator = selenium.find_element_by_class_name('paginator')
            button = paginator.find_elements_by_tag_name('li')
            act = selenium.find_element_by_css_selector(
                '#page-wrapper .active')
            assert button[i] == act
        dis = selenium.find_element_by_css_selector('#page-wrapper .disabled')
        assert button[6] == dis
    finally:
        selenium.quit()
