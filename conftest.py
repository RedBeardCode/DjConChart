from selenium.webdriver import DesiredCapabilities, Chrome
from selenium.webdriver import Firefox, PhantomJS, Remote


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
