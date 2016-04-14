import datetime

from django.contrib.auth.models import User, Permission
from django.core.files.base import ContentFile

from MeasurementManagement.models import MeasurementDevice, MeasurementItem, CalculationRule
from MeasurementManagement.models import MeasurementOrder, MeasurementOrderDefinition, CharacteristicValueDescription, \
    MeasurementTag, Measurement, Product

FAKE_TIME = datetime.datetime(2020, 12, 5, 17, 5, 55)


def create_limited_users():
    limited_user = User.objects.create(username='limited_user')
    limited_user.set_password('test')
    limited_user.save()
    change_user = User.objects.create(username='change_user')
    change_user.set_password('test')
    change_permissions = Permission.objects.filter(codename__contains='change')
    change_user.user_permissions = change_permissions
    change_user.save()
    delete_user = User.objects.create(username='delete_user')
    delete_user.set_password('test')
    delete_permissions = Permission.objects.filter(codename__contains='delete')
    delete_user.user_permissions = delete_permissions
    delete_user.save()


def login_as_limited_user(selenium, user='limited_user'):
    username = selenium.find_element_by_id('id_username')
    pwd = selenium.find_element_by_id('id_password')
    username.send_keys(user)
    pwd.send_keys('test')
    selenium.find_element_by_tag_name('form').submit()

def login_as_admin(selenium):
    username = selenium.find_element_by_id('id_username')
    pwd = selenium.find_element_by_id('id_password')
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

def create_correct_sample_data():
    dummy = MeasurementTag.objects.create(name='width')
    dummy = MeasurementTag.objects.create(name='height')
    calc_rule = CalculationRule.objects.create(rule_name="calc_rule", rule_code=CALC_RULE_CODE)
    calc_multi_rule = CalculationRule.objects.create(rule_name="calc_multi_rule",
                                                     rule_code=CALC_MULTI_RULE_CODE)
    devices = [MeasurementDevice.objects.create(sn=i, name='Device {:d}'.format(i)) for i in range(5)]
    length = CharacteristicValueDescription.objects.create(value_name='length', description='length',
                                                           calculation_rule=calc_rule)
    length.possible_meas_devices.add(devices[0])
    width = CharacteristicValueDescription.objects.create(value_name='width', description='width',
                                                          calculation_rule=calc_rule)
    width.possible_meas_devices.add(*(devices[:3]))
    height = CharacteristicValueDescription.objects.create(value_name='height', description='height',
                                                           calculation_rule=calc_multi_rule)
    height.possible_meas_devices.add(*devices)

    products = []
    products.append(Product.objects.create(product_name='product1'))
    products.append(Product.objects.create(product_name='product2'))
    products.append(Product.objects.create(product_name='product3'))

    order_definition1 = MeasurementOrderDefinition.objects.create(name="OrderDefinition1", product=products[0])
    order_definition1.characteristic_values.add(length)
    order_definition2 = MeasurementOrderDefinition.objects.create(name="OrderDefinition2", product=products[1])
    order_definition2.characteristic_values.add(length, width)
    order_definition3 = MeasurementOrderDefinition.objects.create(name="OrderDefinition3", product=products[2])
    order_definition3.characteristic_values.add(length, width, height)
    order_definitions = [order_definition1, order_definition2, order_definition3]
    for i in range(10):
        item = MeasurementItem.objects.create(sn='{:07d}'.format(i), name='Item {:d}'.format(i),
                                              product=products[i % 3])
        order = MeasurementOrder.objects.create(order_type=order_definitions[i % 3])
        order.measurement_items.add(item)


def create_sample_characteristic_values():
    orders = MeasurementOrder.objects.all()
    count = 0
    for order in orders:
        cv_types = order.order_type.characteristic_values.all()
        user = User.objects.all()[0]
        item = order.measurement_items.all()[0]
        for cv_type in cv_types:
            meas = Measurement.objects.create(date=datetime.datetime.now(), order=order,
                                              meas_item=item, examiner=user)
            meas.measurement_devices.add(cv_type.possible_meas_devices.all()[0])
            meas.order_items.add(cv_type)
            meas.remarks = str(cv_type)
            meas.raw_data_file = ContentFile('erste_messung.txt')
            meas.save()
            count += 1

