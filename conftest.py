#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Configuration of the pytest with CmdLine options, Fixtures and TearDown
function
"""

import os

import pytest
from django.conf import settings
from selenium.webdriver import DesiredCapabilities, Chrome
from selenium.webdriver import Firefox, PhantomJS, Remote

from control_chart.tests.utilies import create_correct_sample_data
from control_chart.tests.utilies import create_limited_users, login_as_admin
from control_chart.tests.utilies import create_characteristic_values


def pytest_addoption(parser):
    """
    Add the different Browser engines as cmd line option
    """
    parser.addoption('--phantomjs', action="store_true",
                     help='Use PhantomJS Webdriver instead of FireFox')
    parser.addoption('--htmlunit', action="store_true",
                     help='Use HtmlUnit Webdriver instead of FireFox')
    parser.addoption('--chrome', action="store_true",
                     help='Use Google Chrome Webdriver instead of FireFox')
    parser.addoption('--ci', action="store_true",
                     help='Using the chrome on sauce lab')


class HtmlUnit(Remote):
    """
    Wrapper class for the HtmlUnit Webdriver to set the server address
    """
    def __init__(self):
        super(HtmlUnit, self).__init__('http://127.0.0.1:4444/wd/hub',
                                       DesiredCapabilities.HTMLUNITWITHJS)


class SauceLab(Remote):
    """
    Wrapper class for the Remote Webdriver for using SauceLab
    """
    def __init__(self, request=None):
        tunnel_id = os.environ['TRAVIS_JOB_NUMBER']
        browser = os.environ['SAUCE_BROWSER']
        platform = os.environ['SAUCE_PLATFORM']
        desired_cap = {
            'platform': platform,
            'browserName': browser,
            'tunnelIdentifier': tunnel_id
        }
        if request:
            desired_cap['name'] = request.node.nodeid
        user = os.environ['SAUCE_USERNAME']
        key = os.environ['SAUCE_ACCESS_KEY']
        url = 'http://{0}:{1}@ondemand.saucelabs.com/wd/hub'.format(user, key)
        super(SauceLab, self).__init__(url, desired_cap)


def pytest_generate_tests(metafunc):
    """
    Processes the new CmdLine Options
    """
    if 'webdriver' in metafunc.fixturenames:
        if metafunc.config.option.phantomjs:
            metafunc.parametrize(['webdriver'], ((PhantomJS,),))
        elif metafunc.config.option.htmlunit:
            metafunc.parametrize(['webdriver'], ((HtmlUnit,),))
        elif metafunc.config.option.chrome:
            metafunc.parametrize(['webdriver'], ((Chrome,),))
        elif metafunc.config.option.ci:
            metafunc.parametrize(['webdriver'], ((SauceLab,),))
        else:
            metafunc.parametrize(['webdriver'], ((Firefox,),))


@pytest.fixture
def fix_webdriver(request):
    """
    Browser engine fixutre for use in working_instance fixture
    """
    webdriver = Firefox
    if request.config.getoption('phantomjs'):
        webdriver = PhantomJS
    elif request.config.getoption('chrome'):
        webdriver = Chrome
    elif request.config.getoption('htmlunit'):
        webdriver = HtmlUnit
    elif request.config.getoption('ci'):
        webdriver = lambda: SauceLab(request)  # # noqa
    return webdriver


@pytest.fixture
def test_data():
    """
    Creates test data in the database
    """
    create_correct_sample_data()
    create_limited_users()
    create_characteristic_values()


@pytest.fixture
def working_instance(request, live_server,
                     fix_webdriver,      # pylint: disable=W0621
                     transactional_db,  # pylint: disable=W0613
                     test_data):  # pylint: disable=W0613,W0621
    """
    Create ready to use testing enviroment, with sample datas in the db and
    webdriver instance which is logged in as admin
    """
    def fin(selenium):
        """
        Close the Webdriver
        """
        selenium.quit()

    selenium = fix_webdriver()
    selenium.get(live_server.url)
    login_as_admin(selenium)
    request.addfinalizer(lambda: fin(selenium))
    return selenium


@pytest.fixture(scope='session')
def bokeh_server(request):
    """
    Fixture to start the bokeh server, the fixture is session scoped so the
    server starts only once per session
    """
    from subprocess import Popen
    os.environ['BOKEH_SERVER'] = 'http://localhost:6008/'
    server = Popen(['bokeh', 'serve',
                    '--port=6008',
                    '--allow-websocket-origin=localhost:8081',
                    '--allow-websocket-origin=127.0.0.1:8081',
                    '--allow-websocket-origin=localhost:8082',
                    '--allow-websocket-origin=127.0.0.1:8082'])

    def fin(server):
        """
        Stops the bokeh server
        """
        server.terminate()

    request.addfinalizer(lambda: fin(server))
    return None


def pytest_runtest_teardown(item):
    """
    Teardown function to delete all create measurement raw data files
    """
    if item.get_marker('django_db') and \
            os.path.exists(settings.MEASUREMENT_FILE_DIR):
        for file in os.listdir(settings.MEASUREMENT_FILE_DIR):
            os.remove(os.path.join(settings.MEASUREMENT_FILE_DIR, file))
