import pytest

from .utilies import login_as_admin
from ..models import Product


@pytest.mark.django_db
def test_create_product_view(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_product/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_product_name')
        name.send_keys('test_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/'
        assert len(Product.objects.all()) == 1
    finally:
        selenium.close()


@pytest.mark.django_db
def test_create_product_view_noname(admin_client, live_server, webdriver):
    selenium = webdriver()
    try:
        selenium.get(live_server + '/new_product/')
        login_as_admin(selenium)
        name = selenium.find_element_by_id('id_product_name')
        selenium.find_element_by_tag_name('form').submit()
        assert selenium.current_url == live_server + '/new_product/'
        assert len(Product.objects.all()) == 0
    finally:
        selenium.close()
