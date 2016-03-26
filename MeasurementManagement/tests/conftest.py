from selenium.webdriver import Firefox, PhantomJS


def pytest_addoption(parser):
    parser.addoption('--phantomjs', default=None, help='Use PhantomJS Webdriver instead of FireFox')


def pytest_generate_tests(metafunc):
    if 'webdriver' in metafunc.fixturenames:
        if metafunc.config.option.phantomjs:
            metafunc.parametrize(['webdriver'], ((PhantomJS,),))
        else:
            metafunc.parametrize(['webdriver'], ((Firefox,),))
