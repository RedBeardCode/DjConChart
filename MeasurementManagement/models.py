from django.db import models
from django.contrib.auth.models import User
from django.db import transaction
import reversion as revisions
# Create your models here.

class MeasurementDevice(models.Model):
    name = models.CharField(max_length=127)
    sn = models.CharField(max_length=11)

    def __unicode__(self):
        return self.name + ": " + self.sn

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'


@revisions.register
class CalculationRule(models.Model):
    rule_name = models.TextField(verbose_name='Name of the calculation rule')
    rule_code = models.TextField(verbose_name='Python code for the analysis')

    def __init__(self, *args, **kwargs):
        super(CalculationRule, self).__init__(*args, **kwargs)
        self.__is_changed = True

    def __unicode__(self):
        return self.rule_name

    def __str__(self):
        return str(self.__unicode__())


    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.rule_name + '>'

    def calculate(self, measurements):
        func_name = '__calc_rule_function_{:d}'.format(self.pk)
        code_lines = ['def ' + func_name + '(measurements):'] + ['    ' + line for line in self.rule_code.splitlines()]
        code_lines += ['    return calculate(measurements)']
        exec('\n'.join(code_lines))
        self.__calc_func = locals()[func_name]
        self.__is_changed = False
        return self.__calc_func(measurements)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.__is_changed = True
        with transaction.atomic(), revisions.create_revision():
            super(CalculationRule, self).save(force_insert, force_update, using, update_fields)

    def is_changed(self):
        return self.__is_changed

class CharacteristicValueDescription(models.Model):
    value_name = models.CharField(max_length=127, verbose_name='Name of the characterisitc value')
    description = models.TextField(verbose_name='Description of the characteristic value')
    calculation_rule = models.ForeignKey(CalculationRule)
    possible_meas_devices = models.ManyToManyField(MeasurementDevice)

    def __unicode__(self):
        return  self.value_name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.value_name + '>'


class MeasurementItem(models.Model):
    sn = models.CharField(max_length=11, verbose_name='Serial number of the measurement item')
    name = models.CharField(max_length=255, verbose_name='Name of the measurement item', blank=True)

    def __unicode__(self):
        return  self.name + ': ' + self.sn

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'


class MeasurementOrderDefinition(models.Model):
    name = models.CharField(max_length=127, verbose_name='Name of the measurement order')
    characteristic_values = models.ManyToManyField(CharacteristicValueDescription,
                                                   verbose_name='Characterisctic values to be measured')
    def __unicode__(self):
        return  self.name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'

class MeasurementOrder(models.Model):
    order_type = models.ForeignKey(MeasurementOrderDefinition, verbose_name='Based measurement order definition')
    measurement_items = models.ManyToManyField(MeasurementItem, verbose_name='Measured items')

    def __unicode__(self):
        return self.order_type.name + ' from ' + str(self.date)

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'




class Measurement(models.Model):
    date = models.DateTimeField(verbose_name='Date of the measurement')
    order = models.ForeignKey(MeasurementOrder, verbose_name='Measurement order')
    order_items = models.ManyToManyField(CharacteristicValueDescription, verbose_name='Item of the measurement order')
    examiner = models.ForeignKey(User)
    remarks = models.TextField(blank=True, verbose_name='Remarks')
    meas_item = models.ForeignKey(MeasurementItem, verbose_name='Measurement item')
    measurement_devices = models.ManyToManyField(MeasurementDevice, verbose_name='Used measurement devices')
    raw_data_file = models.FileField(verbose_name='Raw data file')

    def __unicode__(self):
        return "Measurement form " + str(self.date)

    def __str__(self):
        return str(self.__unicode__())

class CharacteristicValue(models.Model):
    value_type = models.ForeignKey(CharacteristicValueDescription)
    measurements = models.ManyToManyField(Measurement)

    def __init__(self, *args, **kwargs):
        super(CharacteristicValue, self).__init__(*args,**kwargs)
        self.__calc_value = None
        self.__calc_rule = None

    @property
    def value(self):
        if self.__calc_value and self.__calc_rule == self.value_type.calculation_rule:
            return self.__calc_value
        return self.__calculate_value()

    def __calculate_value(self):
        self.__calc_rule = self.value_type.calculation_rule
        self.__calc_value = self.__calc_rule.calculate(self.measurements)
        return self.__calc_value

    def get_value_type_name(self):
        return self.value_type.value_name

    def __unicode__(self):
        return self.value_type.value_name + ': ' + str(self.value)

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.value_type.value_name + ': ' + str(self.value) + '>'
