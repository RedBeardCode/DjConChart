#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest
from selenium.webdriver import PhantomJS
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class TestBaseLayout(object):
    def test_top_navbar(self, working_instance):  # pylint: disable=R0201
        if isinstance(working_instance, PhantomJS):
            pytest.xfail("is_displayed doesn't works correct in PhantomJS")
        list_elements = working_instance.find_elements_by_css_selector(
            '.navbar-top-links li')
        assert len(list_elements) == 2
        assert list_elements[0].is_displayed()
        assert not list_elements[1].is_displayed()
        assert not working_instance.find_element_by_css_selector(
            '.navbar-header button').is_displayed()
        working_instance.set_window_size(600, 1000)
        list_elements = working_instance.find_elements_by_css_selector(
            '.navbar-top-links li')
        assert list_elements[0].is_displayed()
        assert not list_elements[1].is_displayed()
        assert working_instance.find_element_by_css_selector(
            '.navbar-header button').is_displayed()

    def test_side_navbar(self, working_instance):  # pylint: disable=R0201
        if isinstance(working_instance, PhantomJS):
            pytest.xfail("is_displayed doesn't works correct in PhantomJS")
        list_elements = working_instance.find_elements_by_css_selector(
            '.sidebar li')
        assert len(list_elements) == 14
        assert [l.is_displayed() for l in list_elements] == \
               [True] * 8 + [False] * 4 + [True, False]
        working_instance.set_window_size(600, 1000)
        list_elements = working_instance.find_elements_by_css_selector(
            '.sidebar li')
        assert [l.is_displayed() for l in list_elements] == [False] * 14
        button = working_instance.find_element_by_css_selector(
            '.navbar-header button')
        button.click()
        wait = WebDriverWait(working_instance, 5)
        for element in list_elements[:8]:
            wait.until(EC.visibility_of(element))
        list_elements = working_instance.find_elements_by_css_selector(
            '.sidebar li')
        assert [l.is_displayed() for l in list_elements] == \
               [True] * 8 + [False] * 4 + [True, False]
        list_elements[7].click()
        for element in list_elements[8:12]:
            wait.until(EC.visibility_of(element))
        list_elements = working_instance.find_elements_by_css_selector(
            '.sidebar li')
        assert [l.is_displayed() for l in list_elements] == [True] * 12 + \
                                                            [True, False]
        list_elements[12].click()
        for element in list_elements[8:12]:
            wait.until_not(EC.visibility_of(element))

        wait.until(EC.visibility_of(list_elements[13]))
        list_elements = working_instance.find_elements_by_css_selector(
            '.sidebar li')
        assert [l.is_displayed() for l in list_elements] == [True] * 8 +\
                                                            [False] * 4 + \
                                                            [True] * 2

    def test_side_navbar_links(self, live_server, working_instance):  # pylint: disable=R0201
        links = working_instance.find_elements_by_css_selector('.sidebar a')
        for link, href in zip(
                links,
                [live_server + '/',
                 live_server + '/plot_configuration/',
                 live_server + '/measurement/',
                 live_server + '/measurement_item/',
                 live_server + '/measurement_order/',
                 live_server + '/measurement_device/',
                 live_server + '/product/',
                 live_server + '/#',
                 live_server + '/measurement_tag/',
                 live_server + '/characteristic_value_definition/',
                 live_server + '/measurement_order_definition/',
                 live_server + '/calculation_rule/',
                 live_server + '/#',
                 live_server + '/recalc_characteristic_values/']):
            assert link.get_attribute('href') == href
