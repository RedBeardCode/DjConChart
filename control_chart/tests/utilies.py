#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Functions to create test data in the database
for unit tests and development
"""

import os
from random import random

from django.conf import settings
from django.contrib.auth.models import User, Permission, Group
from django.core.files.base import File
from django.utils import timezone


from ..models import Measurement
from ..models import MeasurementDevice, MeasurementItem, CalculationRule
from ..models import MeasurementOrder, MeasurementOrderDefinition, Product
from ..models import PlotConfig, MeasurementTag, CharacteristicValueDefinition

FAKE_TIME = timezone.datetime(2020, 12, 5, 17, 5, 55)


def create_grouped_users():
    """
    Creates test user and user groups
    """
    viewer = User.objects.get_or_create(username='Viewer')[0]
    viewer.groups.add(Group.objects.get(name='Viewer'))
    viewer.set_password('test')
    viewer.save()
    examiner = User.objects.get_or_create(username='Examiner')[0]
    examiner.groups.add(Group.objects.get(name='Examiner'))
    examiner.set_password('test')
    examiner.save()
    manager = User.objects.get_or_create(username='Manager')[0]
    manager.groups.add(Group.objects.get(name='Manager'))
    manager.set_password('test')
    manager.save()
    admin = User.objects.get_or_create(username='Administrator')[0]
    admin.groups.add(Group.objects.get(name='Administrator'))
    admin.set_password('test')
    admin.save()


def create_limited_users():
    """
    Creates users with different privileges (limit, add, change, remove, admin)
    """
    limited_user = User.objects.get_or_create(username='limited_user')[0]
    limited_user.set_password('test')
    limited_user.save()
    add_user = User.objects.get_or_create(username='add_user')[0]
    add_user.set_password('test')
    add_permissions = Permission.objects.filter(codename__contains='add')
    add_user.user_permissions = add_permissions
    add_user.save()
    change_user = User.objects.get_or_create(username='change_user')[0]
    change_user.set_password('test')
    change_permissions = Permission.objects.filter(codename__contains='change')
    change_user.user_permissions = change_permissions
    change_user.save()
    delete_user = User.objects.get_or_create(username='delete_user')[0]
    delete_user.set_password('test')
    delete_permissions = Permission.objects.filter(codename__contains='delete')
    delete_user.user_permissions = delete_permissions
    delete_user.save()
    super_user = User.objects.get_or_create(username='admin')[0]
    super_user.set_password('password')
    super_user.is_superuser = True
    super_user.save()


def login_as_limited_user(selenium, user='limited_user'):
    """
    Logs in the given selenium webdriver instance as user with the given
    privileges
    """
    username = selenium.find_element_by_id('id_username')
    pwd = selenium.find_element_by_id('id_password')
    username.send_keys(user)
    pwd.send_keys('test')
    selenium.find_element_by_tag_name('form').submit()


def login_as_admin(selenium):
    """
    Logs in the given selenium webdriver instance as admin user
    """
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.support.ui import WebDriverWait
    username = WebDriverWait(selenium, 5).until(
        EC.presence_of_element_located((By.ID, 'id_username')))
    pwd = WebDriverWait(selenium, 5).until(
        EC.presence_of_element_located((By.ID, 'id_password')))
    username.send_keys('admin')
    pwd.send_keys('password')
    selenium.find_element_by_tag_name('form').submit()


CALC_RULE_CODE = '''
def calculate(meas_dict):
    return 1.0\n'''

CALC_MULTI_RULE_CODE = '''
def calculate(meas_dict):
    if "width" in meas_dict and "height" in meas_dict:
        return 42
    else:
        return None
'''


def wait_for_root_page(selenium):
    """
    Waits until the start page is shown
    """
    selenium.implicitly_wait(5)
    selenium.find_element_by_css_selector('#page-wrapper h1')


def create_correct_sample_data():
    """
    Creates a set of sample test data (MeasurementTag, CalculationRule,
    MeasurementDevice, CharacteristicValueDefinition, Product,
    MeasurementOrderDefinition, MeasurementOrder, MesasurementItem)
    """
    dummy = MeasurementTag.objects.get_or_create(name='width')
    dummy = MeasurementTag.objects.get_or_create(name='height')
    calc_rule = CalculationRule.objects.get_or_create(
        rule_name="calc_rule", rule_code=CALC_RULE_CODE)[0]
    calc_multi_rule = CalculationRule.objects.get_or_create(
        rule_name="calc_multi_rule", rule_code=CALC_MULTI_RULE_CODE)[0]
    devices = [MeasurementDevice.objects.get_or_create(
        serial_nr=i, name='Device {:d}'.format(i))[0] for i in range(5)]
    length = CharacteristicValueDefinition.objects.get_or_create(
        value_name='length', description='length',
        calculation_rule=calc_rule)[0]
    length.possible_meas_devices.add(devices[0])
    width = CharacteristicValueDefinition.objects.get_or_create(
        value_name='width', description='width', calculation_rule=calc_rule)[0]
    width.possible_meas_devices.add(*(devices[:3]))
    height = CharacteristicValueDefinition.objects.get_or_create(
        value_name='height', description='height',
        calculation_rule=calc_multi_rule)[0]
    height.possible_meas_devices.add(*devices)

    products = []
    products.append(Product.objects.get_or_create(product_name='product1')[0])
    products.append(Product.objects.get_or_create(product_name='product2')[0])
    products.append(Product.objects.get_or_create(product_name='product3')[0])

    order_definition1 = MeasurementOrderDefinition.objects.get_or_create(
        name="OrderDefinition1", product=products[0])[0]
    order_definition1.characteristic_values.add(length)
    order_definition2 = MeasurementOrderDefinition.objects.get_or_create(
        name="OrderDefinition2", product=products[1])[0]
    order_definition2.characteristic_values.add(length, width)
    order_definition3 = MeasurementOrderDefinition.objects.get_or_create(
        name="OrderDefinition3", product=products[2])[0]
    order_definition3.characteristic_values.add(length, width, height)
    order_definitions = [order_definition1,
                         order_definition2,
                         order_definition3]
    for i in range(10):
        item = MeasurementItem.objects.create(
            serial_nr='{:07d}'.format(i), name='Item {:d}'.format(i),
            product=products[i % 3])
        order = MeasurementOrder.objects.create(
            order_type=order_definitions[i % 3])
        order.measurement_items.add(item)


def create_characteristic_values():
    """
    Creates Measurements and so CharateristicValues will be created
    automatically
    """
    orders = MeasurementOrder.objects.all()
    for order in orders:
        item = order.measurement_items.all()[0]
        create_new_measurement(order, item)


def create_new_measurement(order, meas_item, cv_type_ids=None):
    """
    Creates a new test measurement for the given measurement order,
    measurement item and Characteristic value type. If the characteristic
    value type is None measurements for all types in the measurement order
    will be created
    """
    user = User.objects.all()[0]
    cv_types = order.order_type.characteristic_values.all()
    if cv_type_ids:
        cv_types = [cv_types[i] for i in cv_type_ids]
    for cv_type in cv_types:
        kwargs = {'date': timezone.now(), 'order': order,
                  'meas_item': meas_item, 'examiner': user}
        meas = Measurement.objects.get_or_create(**kwargs)[0]
        if hasattr(Measurement, 'position'):
            from django.contrib.gis.geos import GEOSGeometry
            long = 3 * random() / 10.0
            lat = 3 * random() / 10.0
            position = GEOSGeometry('SRID=4326;POINT({0} {1})'.format(
                7 + long, 50 + lat))
            meas.position = position
        meas.measurement_devices.add(
            cv_type.possible_meas_devices.all()[0])
        meas.order_items.add(cv_type)
        meas.remarks = str(cv_type)
        raw_filename = os.path.join(settings.BASE_DIR,
                                    'samples_rsc/erste_messung.txt')
        meas.raw_data_file = File(open(raw_filename, 'r'))
        meas.save()


def create_item_order_meas(order_type, product):
    """
    Helper to create a measurement item, measurement order and measurement for
    the given measurement order definition and product.
    """
    serial_nr = int(random() * 1e10)
    name = '{0}: {1}'.format(product.product_name, serial_nr)
    item = MeasurementItem.objects.get_or_create(product=product,
                                                 serial_nr=serial_nr,
                                                 name=name)[0]
    item.save()
    order = MeasurementOrder.objects.create(order_type=order_type)
    order.measurement_items.add(item)
    order.save()
    create_new_measurement(order, item)


def create_plot_config():
    """
    Creates a set of test PlotConfig
    """
    gt05 = PlotConfig.objects.get_or_create(description='Greater 0.5',
                                            short_name='gt05')[0]
    gt05.filter_args = [{'value__gt': 0.5}]
    gt05.titles = 'Greater than 0.5'
    gt05.save()
    le05 = PlotConfig.objects.get_or_create(description='Less equal 0.5',
                                            short_name='lte05')[0]
    le05.filter_args = [{'value__lte': 0.5}]
    le05.titles = 'Lower equal than 0.5'
    le05.save()
    multi = PlotConfig.objects.get_or_create(description='Multline',
                                             short_name='multi')[0]
    multi.filter_args = [{'value_type__value_name': 'length'},
                         {'value_type__value_name': 'width'}]
    multi.titles = ['length', 'width']
    multi.save()
