import pickle
from re import compile

import reversion as revisions
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.db.models import Q
from django.db.models.signals import post_save
from django_pandas.io import read_frame
from django_pandas.managers import DataFrameQuerySet

# Create your models here.
from MeasurementManagement.plot_annotation import PlotAnnotationContainer


class Product(models.Model):
    product_name = models.CharField(max_length=30, unique=True)

    def __unicode__(self):
        return self.product_name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.product_name + ' >'


class MeasurementDevice(models.Model):
    name = models.CharField(max_length=127)
    sn = models.CharField(max_length=11)

    def __unicode__(self):
        return self.name + ": " + self.sn

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'


class AccessLogDict(dict):
    def __init__(self, *args, **kwargs):
        super(AccessLogDict, self).__init__(*args, **kwargs)
        self.__read_keys = set()

    def __contains__(self, item):
        self.__read_keys.add(item)
        return super(AccessLogDict, self).__contains__(item)

    def __getitem__(self, item):
        self.__read_keys.add(item)
        return super(AccessLogDict, self).__getitem__(item)

    def get_missing_keys(self):
        missing_keys = set()
        for key in self.__read_keys:
            if key not in self.keys():
                missing_keys.add(key)
        return missing_keys


@revisions.register
class CalculationRule(models.Model):
    rule_name = models.TextField(verbose_name='Name of the calculation rule')
    rule_code = models.TextField(verbose_name='Python code for the analysis')

    def __init__(self, *args, **kwargs):
        super(CalculationRule, self).__init__(*args, **kwargs)
        self.__is_changed = True
        self.__missing_keys = set()

    def __unicode__(self):
        return self.rule_name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.rule_name + '>'

    @property
    def missing_keys(self):
        return self.__missing_keys

    def calculate(self, measurements):
        meas_dict = AccessLogDict()
        for meas in measurements.all():
            if meas.measurement_tag:
                meas_dict[meas.measurement_tag.name] = meas
            else:
                meas_dict[''] = meas
        func_name = '__calc_rule_function_{:d}'.format(self.pk)
        code_lines = ['def ' + func_name + '(meas_dict):'] + ['    ' + line for line in self.rule_code.splitlines()]
        code_lines += ['    return calculate(meas_dict)']
        exec('\n'.join(code_lines))
        self.__calc_func = locals()[func_name]
        self.__is_changed = False
        calc_return = self.__calc_func(meas_dict)
        self.__missing_keys = meas_dict.get_missing_keys()
        return calc_return

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.__is_changed = True
        with transaction.atomic(), revisions.create_revision():
            super(CalculationRule, self).save(force_insert, force_update, using, update_fields)
        CharacteristicValue.objects.filter(value_type__calculation_rule__rule_name=self.rule_name).update(
            _is_valid=False)

    def is_changed(self):
        return self.__is_changed


class MeasurementTag(models.Model):
    name = models.CharField(max_length=255, verbose_name='Tag to distingish measurements for one characteristic value')

    def __unicode__(self):
        return self.name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.name + '>'


class CharacteristicValueDescription(models.Model):
    value_name = models.CharField(max_length=127, verbose_name='Name of the characterisitc value')
    description = models.TextField(verbose_name='Description of the characteristic value')
    calculation_rule = models.ForeignKey(CalculationRule)
    possible_meas_devices = models.ManyToManyField(MeasurementDevice)
    #Ich denke unnötig
    # measurement_tags = models.ManyToManyField(MeasurementTag, blank=True)
    def __unicode__(self):
        return  self.value_name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.value_name + '>'


class MeasurementItem(models.Model):
    sn = models.CharField(max_length=11, verbose_name='Serial number of the measurement item')
    name = models.CharField(max_length=255, verbose_name='Name of the measurement item', blank=True)
    product = models.ForeignKey(Product, verbose_name='Product')
    def __unicode__(self):
        return  self.name + ': ' + self.sn

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'


class MeasurementOrderDefinition(models.Model):
    name = models.CharField(max_length=127, verbose_name='Name of the measurement order')
    product = models.ForeignKey(Product, verbose_name='Product to be measured')
    characteristic_values = models.ManyToManyField(CharacteristicValueDescription,
                                                   verbose_name='Characterisctic values to be measured')

    def __unicode__(self):
        return  self.name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'


class MeasurementOrder(models.Model):
    order_nr = models.AutoField(primary_key=True)
    order_type = models.ForeignKey(MeasurementOrderDefinition, verbose_name='Based measurement order definition')
    measurement_items = models.ManyToManyField(MeasurementItem, verbose_name='Measured items')
    def __unicode__(self):
        items_str = ''
        for item in self.measurement_items.all():
            items_str += str(item) + ', '
        return self.order_type.name + ' ' + str(self.order_nr) + ' for ' + items_str

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__unicode__() + '>'


def after_measurement_saved(instance, **kwargs):
    for value_type in instance.order_items.all():
        ch_value, created = CharacteristicValue.objects.get_or_create(order=instance.order, value_type=value_type)
        ch_value.measurements.add(instance)
        ch_value.save()


class Measurement(models.Model):
    date = models.DateTimeField(verbose_name='Date of the measurement')
    order = models.ForeignKey(MeasurementOrder, verbose_name='Measurement order')
    order_items = models.ManyToManyField(CharacteristicValueDescription, verbose_name='Item of the measurement order')
    examiner = models.ForeignKey(User)
    remarks = models.TextField(blank=True, verbose_name='Remarks')
    meas_item = models.ForeignKey(MeasurementItem, verbose_name='Measurement item')
    measurement_devices = models.ManyToManyField(MeasurementDevice, verbose_name='Used measurement devices')
    raw_data_file = models.FileField(verbose_name='Raw data file')

    measurement_tag = models.ForeignKey(MeasurementTag, blank=True, null=True)

    def __unicode__(self):
        return "Measurement from " + str(self.date)

    def __str__(self):
        return str(self.__unicode__())


post_save.connect(after_measurement_saved, sender=Measurement)


def after_characteristic_value_saved(instance, update_fields, **kwargs):
    if not update_fields or 'measurements' in update_fields:
        dummy = instance.value


class CalcValueQuerySet(DataFrameQuerySet):
    value_re = compile('^value([_]{2})')
    MAX_NUM_CALCULATION = 100

    def __init__(self, *args, **kwargs):
        super(CalcValueQuerySet, self).__init__(*args, **kwargs)

    def filter(self, *args, **kwargs):
        for query in args:
            if isinstance(query, Q):
                for index, exp in enumerate(query.children):
                    if isinstance(exp, tuple):
                        query.children[index] = (self.value_re.sub('_calc_value\g<1>', exp[0]), exp[1])
        for key in kwargs:
            if key.startswith('value'):
                new_key = self.value_re.sub('_calc_value\g<1>', key)
                kwargs[new_key] = kwargs.pop(key)
        return super(CalcValueQuerySet, self).filter(*args, **kwargs)

    def recalculation(self):
        for value in self:
            dummy = value.value

    def to_dataframe(self, fieldnames=(), verbose=True, index=None,
                     coerce_float=False):
        outdated_values = self.filter(_is_valid=False)
        if self.filter(_is_valid=False).count() > self.MAX_NUM_CALCULATION:
            raise UserWarning('More then {} characteristic values have to be recalculated for this request.\n'
                              'Please recalcutate the values manually (RecalcView) first')
        outdated_values.recalculation()
        read_calc_value = '_calc_value' in fieldnames
        if 'value' in fieldnames:
            fieldnames[fieldnames.index('value')] = '_calc_value'
        frame = read_frame(self, fieldnames=fieldnames, verbose=verbose,
                           index_col=index, coerce_float=coerce_float)
        if '_calc_value' in frame.columns and not read_calc_value:
            new_labels = list(frame.columns)
            new_labels[new_labels.index('_calc_value')] = 'value'
            frame.columns = new_labels
        return frame


CalcValueManager = models.Manager.from_queryset(CalcValueQuerySet)

class CharacteristicValue(models.Model):
    order = models.ForeignKey(MeasurementOrder)
    value_type = models.ForeignKey(CharacteristicValueDescription)
    measurements = models.ManyToManyField(Measurement)
    date = models.DateTimeField(auto_now_add=True)
    _is_valid = models.BooleanField(default=False)
    _finished = models.BooleanField(default=False)
    _calc_value = models.FloatField(blank=True, null=True)

    objects = CalcValueManager()

    class Meta:
        unique_together = ['order', 'value_type']
        ordering = ['date']

    def __init__(self, *args, **kwargs):
        if 'order' in kwargs and 'value_type' in kwargs:
            order = kwargs['order']
            value_type = kwargs['value_type']
            if value_type not in order.order_type.characteristic_values.all():
                raise ValidationError('Characteristic Value is not demanded in order')
        super(CharacteristicValue, self).__init__(*args,**kwargs)


    @property
    def value(self):
        if self.is_valid and self._finished:
            return self._calc_value
        return self.__calculate_value()

    def __calculate_value(self):
        if self.measurements.count() < 1:
            return None
        calc_value = self.value_type.calculation_rule.calculate(self.measurements)
        self._is_valid = True
        if calc_value:
            self._calc_value = calc_value
            self._finished = True
            test = self.measurements.last()
            self.date = self.measurements.last().date
            self.save(update_fields=['_is_valid', '_calc_value', '_finished', 'date'])
        return self._calc_value

    def get_value_type_name(self):
        return self.value_type.value_name

    @property
    def is_valid(self):
        return self._is_valid

    @property
    def missing_keys(self):
        if self._finished:
            return set()
        rule = self.value_type.calculation_rule
        dummy = rule.calculate(self.measurements)
        return rule.missing_keys

    def __unicode__(self):
        return str(self.order.order_nr) + ' ' + self.value_type.value_name

    def __str__(self):
        return str(self.__unicode__())

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.value_type.value_name + ' >'


post_save.connect(after_characteristic_value_saved, sender=CharacteristicValue)


class PlotConfig(models.Model):
    description = models.CharField(max_length=100, verbose_name='Description of the plotted data')
    short_name = models.URLField(verbose_name='Short name of configuration. Also used for url', )
    _filter_args = models.BinaryField(blank=True,
                                      verbose_name='Pickle of list of dictionaries with filter lookup strings')
    _plot_args = models.BinaryField(blank=True, verbose_name='Pickle of List of dictionaries with plot parameter')
    _annotations = models.BinaryField(blank=True, verbose_name='Plot annotations which should be shown')

    def __init__(self, *args, **kwargs):
        super(PlotConfig, self).__init__(*args, **kwargs)
        self.__last_filter_args = None
        self.__last_plot_args = None
        self.__last_annotations = None
    
    @property
    def filter_args(self):
        if not self._filter_args:
            return None
        if not self.__last_filter_args:
            self.__last_filter_args = pickle.loads(self._filter_args)
        return self.__last_filter_args

    @filter_args.setter
    def filter_args(self, filter_args):
        self.__last_filter_args = filter_args
        self._filter_args = pickle.dumps(filter_args)

    @property
    def plot_args(self):
        if not self._plot_args:
            return None
        if not self.__last_plot_args:
            self.__last_plot_args = pickle.loads(self._plot_args)
        return self.__last_plot_args

    @plot_args.setter
    def plot_args(self, plot_args):
        self.__last_plot_args = plot_args
        self._plot_args = pickle.dumps(plot_args)

    @property
    def annotations(self):
        if not self._annotations:
            return None
        if not self.__last_annotations:
            self.__last_annotations = pickle.loads(self._annotations)
        return self.__last_annotations

    @annotations.setter
    def annotations(self, annotations_dict):
        self.__last_annotations = annotations_dict
        self._annotations = pickle.dumps(annotations_dict)

    def get_annotation_container(self):
        if not self.annotations:
            return None
        container = PlotAnnotationContainer(create_default=False)
        for key in self.annotations:
            container.add_annotation(key, self.annotations[key])
        return container

    def refresh_from_db(self, using=None, fields=None, **kwargs):
        self.__last_filter_args = None
        self.__last_plot_args = None
        self.__last_annotations = None
        super(PlotConfig, self).refresh_from_db(using, fields, **kwargs)
