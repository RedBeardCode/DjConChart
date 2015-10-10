import datetime

from MeasurementManagement.models import MeasurementOrder, MeasurementOrderDefinition, CharacteristicValueDescription
from MeasurementManagement.models import MeasurementDevice, MeasurementItem, CalculationRule

FAKE_TIME = datetime.datetime(2020, 12, 5, 17, 5, 55)


def login_as_admin(selenium):
    username = selenium.find_element_by_id('id_username')
    pwd = selenium.find_element_by_id('id_password')
    username.send_keys('admin')
    pwd.send_keys('password')
    selenium.find_element_by_tag_name('form').submit()


def create_correct_sample_data():
    calc_rule = CalculationRule.objects.create(rule_name="dummy", rule_code='def dummy():\n    return True\n')
    devices = [MeasurementDevice.objects.create(sn=i, name='Device {:d}'.format(i)) for i in range(5)]
    length = CharacteristicValueDescription.objects.create(value_name='length', description='length',
                                                           calculation_rule=calc_rule)
    length.possible_meas_devices.add(devices[0])
    width = CharacteristicValueDescription.objects.create(value_name='width', description='width',
                                                          calculation_rule=calc_rule)
    width.possible_meas_devices.add(*(devices[:3]))
    height = CharacteristicValueDescription.objects.create(value_name='height', description='height',
                                                           calculation_rule=calc_rule)
    height.possible_meas_devices.add(*devices)

    order_definition1 = MeasurementOrderDefinition.objects.create(name="OrderDefinition1")
    order_definition1.charateristic_values.add(length)
    order_definition2 = MeasurementOrderDefinition.objects.create(name="OrderDefinition2")
    order_definition2.charateristic_values.add(length, width)
    order_definition3 = MeasurementOrderDefinition.objects.create(name="OrderDefinition3")
    order_definition3.charateristic_values.add(length, width, height)
    order_definitions = [order_definition1, order_definition2, order_definition3]
    for i in range(10):
        item = MeasurementItem.objects.create(sn=i, name='Item {:d}'.format(i))
        order = MeasurementOrder.objects.create(date=FAKE_TIME + datetime.timedelta(days=i),
                                                order_type=order_definitions[i % 3])
        order.measurement_items.add(item)
