import pytest
from selenium.webdriver import DesiredCapabilities, Chrome
from selenium.webdriver import Firefox, PhantomJS, Remote

from ControlChart.tests.utilies import create_limited_users, create_correct_sample_data, login_as_admin
from ControlChart.tests.utilies import create_sample_characteristic_values


def pytest_addoption(parser):
    parser.addoption('--phantomjs', action="store_true", help='Use PhantomJS Webdriver instead of FireFox')
    parser.addoption('--htmlunit', action="store_true", help='Use HtmlUnit Webdriver instead of FireFox')
    parser.addoption('--chrome', action="store_true", help='Use Google Chrome Webdriver instead of FireFox')


class HtmlUnit(Remote):
    def __init__(self):
        super(HtmlUnit, self).__init__('http://127.0.0.1:4444/wd/hub', DesiredCapabilities.HTMLUNITWITHJS)

def pytest_generate_tests(metafunc):
    if 'webdriver' in metafunc.fixturenames:
        if metafunc.config.option.phantomjs:
            metafunc.parametrize(['webdriver'], ((PhantomJS,),))
        elif metafunc.config.option.htmlunit:
            metafunc.parametrize(['webdriver'], ((HtmlUnit,),))
        elif metafunc.config.option.chrome:
            metafunc.parametrize(['webdriver'], ((Chrome,),))
        else:
            metafunc.parametrize(['webdriver'], ((Firefox,),))


@pytest.fixture
def fix_webdriver(request):
    webdriver = Firefox
    if request.config.getoption('phantomjs'):
        webdriver = PhantomJS
    elif request.config.getoption('chrome'):
        webdriver = Chrome
    elif request.config.getoption('htmlunit'):
        webdriver = HtmlUnit
    return webdriver


@pytest.fixture
def working_instance(request, live_server, fix_webdriver, transactional_db):
    def fin(selenium):
        selenium.quit()

    create_correct_sample_data()
    create_limited_users()
    create_sample_characteristic_values()
    selenium = fix_webdriver()
    selenium.get(live_server.url)
    login_as_admin(selenium)
    request.addfinalizer(lambda: fin(selenium))
    return selenium


@pytest.fixture(scope='session')
def bokeh_server(request):
    from subprocess import Popen
    import os
    os.environ['BOKEH_SERVER'] = 'http://localhost:6008/'
    server = Popen(['bokeh', 'serve',
                    '--port=6008',
                    '--allow-websocket-origin=localhost:8081',
                    '--allow-websocket-origin=127.0.0.1:8081',
                    '--allow-websocket-origin=localhost:8082',
                    '--allow-websocket-origin=127.0.0.1:8082'])

    def fin(server):
        server.terminate()

    request.addfinalizer(lambda: fin(server))
    return None
