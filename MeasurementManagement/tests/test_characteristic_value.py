from datetime import datetime

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
import pytest

from .utilies import create_correct_sample_data
from ..models import CharacteristicValue, MeasurementOrder, Measurement
from ..models import CalculationRule, MeasurementTag, CharacteristicValueDescription


@pytest.mark.django_db
def test_cv_single_creation(admin_client):
    create_correct_sample_data()
    orders = MeasurementOrder.objects.all()
    count = 0
    for order in orders:
        cv_types = order.order_type.characteristic_values.all()
        user = User.objects.get(username='admin')
        item = order.measurement_items.all()[0]
        for cv_type in cv_types:
            meas = Measurement.objects.create(date=datetime.now(), order=order,
                                              meas_item=item, examiner=user)
            meas.measurement_devices.add(cv_type.possible_meas_devices.all()[0])
            meas.order_items.add(cv_type)
            meas.remarks = str(cv_type)
            meas.raw_data_file = ContentFile('erste_messung.txt')
            meas.save()
            count += 1
            assert CharacteristicValue.objects.get(order=order, value_type=cv_type)
    assert len(CharacteristicValue.objects.all()) == count
    assert len(CharacteristicValue.objects.filter(_finished=True)) == count - 3


@pytest.mark.django_db
def test_cv_multi_creation(admin_client):
    create_correct_sample_data()
    orders = MeasurementOrder.objects.filter(order_type__name='OrderDefinition2')
    count = 0
    user = User.objects.get(username='admin')
    for order in orders:
        item = order.measurement_items.all()[0]
        meas = Measurement.objects.create(date=datetime.now(), order=order,
                                          meas_item=item, examiner=user)
        remarks = ''
        for cv_type in order.order_type.characteristic_values.all():
            meas.order_items.add(cv_type)
            meas.measurement_devices.add(cv_type.possible_meas_devices.all()[0])
            remarks += str(cv_type) + '\n'
            count += 1
        meas.remarks = remarks
        meas.raw_data_file = ContentFile('erste_messung.txt')
        meas.save()
    assert len(CharacteristicValue.objects.all()) == count
    for cv in CharacteristicValue.objects.all():
        assert cv._finished
        assert cv.value == 1.0


@pytest.mark.django_db
def test_cv_multi_meas_creation(admin_client):
    create_correct_sample_data()
    orders = MeasurementOrder.objects.filter(order_type__name='OrderDefinition3')
    count = 0
    user = User.objects.get(username='admin')
    for order in orders:
        for cv_type in order.order_type.characteristic_values.filter(value_name='height'):
            item = order.measurement_items.all()[0]
            for tag in MeasurementTag.objects.filter(name__in=['width', 'height']):
                meas = Measurement.objects.create(date=datetime.now(), order=order,
                                                  meas_item=item, examiner=user)
                meas.order_items.add(cv_type)
                meas.measurement_devices.add(cv_type.possible_meas_devices.all()[0])
                count += 1
                meas.remarks = str(cv_type)
                meas.raw_data_file = ContentFile('erste_messung.txt')
                meas.measurement_tag = tag
                meas.save()
    assert len(CharacteristicValue.objects.all()) == count / 2
    for cv in CharacteristicValue.objects.all():
        assert cv._finished
        assert cv.value == 42


CALC_RULE_CODE = '''
def calculate(meas_dict):
    return 2.0\n'''


@pytest.mark.django_db
def test_cv_rule_change(admin_client):
    create_correct_sample_data()
    orders = MeasurementOrder.objects.filter(order_type__name='OrderDefinition1')
    for order in orders:
        cv_types = order.order_type.characteristic_values.all()
        user = User.objects.get(username='admin')
        item = order.measurement_items.all()[0]
        for cv_type in cv_types:
            meas = Measurement.objects.create(date=datetime.now(), order=order,
                                              meas_item=item, examiner=user)
            meas.measurement_devices.add(cv_type.possible_meas_devices.all()[0])
            meas.order_items.add(cv_type)
            meas.remarks = str(cv_type)
            meas.raw_data_file = ContentFile('erste_messung.txt')
            meas.save()
            cv = CharacteristicValue.objects.get(order=order, value_type=cv_type)
            assert cv
            assert cv.value == 1.0
            assert cv._finished
    rule = CalculationRule.objects.get(rule_name='calc_rule')
    rule.rule_code = CALC_RULE_CODE
    rule.save()
    characteristic_values = CharacteristicValue.objects.all()
    for cv in characteristic_values:
        assert cv._calc_value == 1.0
        assert cv.value == 2.0
        assert cv._calc_value == 2.0


@pytest.mark.django_db
def test_cv_wrong_value_type(admin_client):
    create_correct_sample_data()
    orders = MeasurementOrder.objects.filter(order_type__name='OrderDefinition1')
    cv_type = CharacteristicValueDescription.objects.get(value_name='height')
    for order in orders:
        user = User.objects.get(username='admin')
        item = order.measurement_items.all()[0]
        meas = Measurement.objects.create(date=datetime.now(), order=order,
                                          meas_item=item, examiner=user)
        meas.measurement_devices.add(cv_type.possible_meas_devices.all()[0])
        meas.order_items.add(cv_type)
        meas.remarks = str(cv_type)
        meas.raw_data_file = ContentFile('erste_messung.txt')
        with pytest.raises(ValidationError):
            meas.save()
