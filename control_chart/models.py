#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Models for  control_chart
"""

from __future__ import unicode_literals

import os
import pickle
from re import compile as recompile

import reversion as revisions
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.db import transaction
from django.db.models import Q, QuerySet
from django.db.models.signals import post_save, m2m_changed
from django.utils.encoding import python_2_unicode_compatible
from django.utils.html import urlize
from django_pandas.io import read_frame
from django_pandas.managers import DataFrameQuerySet

from control_chart.plot_annotation import PlotAnnotationContainer
from control_chart.plot_util import update_plot_sessions


class ProductQuerySet(QuerySet):
    """
    QuerySet for Product with easy access to the CharacteristicValueDefinitions
    which are linked to one product.
    """
    def __init__(self, *args, **kwargs):
        super(ProductQuerySet, self).__init__(*args, **kwargs)

    def get_charac_value_definitions(self):
        """
        Easy access to the CharacteristicValueDefinitions
        :return: Set of linked CharacteristicValueDefinitions
        """
        value_types = set()
        for prod in self.iterator():
            for mod in prod.measurementorderdefinition_set.all():
                for cvd in mod.characteristic_values.all():
                    value_types.add(cvd)
        return value_types


PRODUCT_MANAGER = models.Manager.from_queryset(ProductQuerySet)  # pylint: disable=E1101


@python_2_unicode_compatible
class Product(models.Model):
    """
    Product to group the MeasurementItems
    """
    product_name = models.CharField(max_length=30, unique=True)

    objects = PRODUCT_MANAGER()

    def __str__(self):
        return self.product_name

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.product_name + ' >'


@python_2_unicode_compatible
class MeasurementDevice(models.Model):
    """
    Measurement device used for the measurement
    """
    name = models.CharField(max_length=127, verbose_name='Device name')
    serial_nr = models.CharField(max_length=11, verbose_name='Serial number')

    def __str__(self):
        return self.name + ": " + self.serial_nr

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__str__() + '>'


@python_2_unicode_compatible
@revisions.register
class CalculationRule(models.Model):
    """
    Calculation (python) code to calculate the characteristic value
    """
    rule_name = models.TextField(verbose_name='Name of the calculation rule')
    rule_code = models.TextField(verbose_name='Python code for the analysis')

    def __init__(self, *args, **kwargs):
        super(CalculationRule, self).__init__(*args, **kwargs)
        self.__is_changed = True
        self.__missing_keys = set()
        self.__calc_func = None

    def __str__(self):
        return self.rule_name

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.rule_name + '>'

    @property
    def missing_keys(self):
        """
        After call of the calculate member it returns the MeasurementTag-Name
        which are missing to calculate the CharacteristicValue yet.
        :return: Set of missing MeasurementTag-Names
        """
        return self.__missing_keys

    def calculate(self, measurements):
        """
        Calculates a CharacteristicValue out of the given Measurements
        :param measurements: List of measurements
        :return: Value for the CharacteristicValue
        """
        meas_dict = AccessLogDict()
        for meas in measurements.all():
            if meas.measurement_tag:
                meas_dict[meas.measurement_tag.name] = meas
            else:
                meas_dict[''] = meas
        func_name = '__calc_rule_function_{:d}'.format(self.pk)
        code_lines = ['def ' + func_name + '(meas_dict):'] + \
                     ['    ' + line for line in self.rule_code.splitlines()]
        code_lines += ['    return calculate(meas_dict)']
        exec('\n'.join(code_lines))  # pylint: disable=W0122
        self.__calc_func = locals()[func_name]
        self.__is_changed = False
        calc_return = self.__calc_func(meas_dict)
        self.__missing_keys = meas_dict.get_missing_keys()
        return calc_return

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        """
        Overrides the method of the base class to mark the linked
        CharacteristicValues as invalid if the CalculationRule has changed
        """
        self.__is_changed = True
        with transaction.atomic(), revisions.create_revision():
            super(CalculationRule, self).save(force_insert, force_update,
                                              using, update_fields)
        CharacteristicValue.objects.filter(
            value_type__calculation_rule__rule_name=self.rule_name).update(
                _is_valid=False)

    def is_changed(self):
        """
        Has the CalculationRule changed
        """
        return self.__is_changed


class AccessLogDict(dict):
    """
    Dict variation which records the access to non existing keys
    """

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
        """
        Returns the non existing keys which have tried to access
        """
        missing_keys = set()
        for key in self.__read_keys:
            if key not in self.keys():
                missing_keys.add(key)
        return missing_keys


@python_2_unicode_compatible
class MeasurementTag(models.Model):
    """
    Tag to differ Measurements for CharacteristicValues which need more then
    one Measurement
    """
    name = models.CharField(max_length=255,
                            verbose_name='Tag to distinguish measurements for'
                                         ' one characteristic value')

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.name + '>'


@python_2_unicode_compatible
class CharacteristicValueDefinition(models.Model):
    """
    Definition of a type of characteristic values
    """
    value_name = models.CharField(
        max_length=127, verbose_name='Name of the characterisitc value')
    description = models.TextField(
        verbose_name='Description of the characteristic value')
    calculation_rule = models.ForeignKey(CalculationRule)
    possible_meas_devices = models.ManyToManyField(MeasurementDevice)

    def __str__(self):
        return self.value_name

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.value_name + '>'


@python_2_unicode_compatible
class MeasurementItem(models.Model):
    """
    Item which is measured
    """
    serial_nr = models.CharField(
        max_length=11, verbose_name='Serial number of the measurement item')
    name = models.CharField(max_length=255,
                            verbose_name='Name of the measurement item',
                            blank=True)
    product = models.ForeignKey(Product, verbose_name='Product')

    def __str__(self):
        return self.name + ': ' + self.serial_nr

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__str__() + '>'


def create_product_plotconfig(instance, **kwargs):
    """
    Creates a configuration for a plot which shows plot for all
    CharacteristicValues of a  product. Called everytime the ManyToManyField
    characteristic_values in a MeasurementOrderDefinition is changed
    :param instance: Changed MeasurementOrderDefinition
    """
    if kwargs['action'] in ['post_add', 'post_remove']:
        cvds = instance.characteristic_values.all()
        plot_config, created = PlotConfig.objects.get_or_create(
            short_name=urlize(instance.product.product_name))
        if created:
            plot_config.description = 'Product view for ' + \
                                      instance.product.product_name
        filter_list = []
        titles = []
        for cvd in cvds:
            filter_entry = {'product__pk': instance.product.pk,
                            'value_type__pk': cvd.pk}
            filter_list.append(filter_entry)
            titles.append(cvd.value_name)
        plot_config.filter_args = filter_list
        plot_config.titles = titles
        plot_config.save()


@python_2_unicode_compatible
class MeasurementOrderDefinition(models.Model):
    """
    Definition of MeasurementOrder to define which CharacteristicValues have to
    be measured for a given MeasurementItem
    """
    name = models.CharField(max_length=127,
                            verbose_name='Name of the measurement order')
    product = models.ForeignKey(Product, verbose_name='Product to be measured')
    characteristic_values = models.ManyToManyField(
        CharacteristicValueDefinition,
        verbose_name='Characteristic values to be measured')

    def __str__(self):
        return self.name

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__str__() + '>'


m2m_changed.connect(
    create_product_plotconfig,
    sender=MeasurementOrderDefinition.characteristic_values.through)  # pylint: disable=E1101


@python_2_unicode_compatible
class MeasurementOrder(models.Model):
    """
    Instance of an MeasurementOrder defined by the MeasurementOrderDefiniton
    """
    order_nr = models.AutoField(primary_key=True, verbose_name='Order number')
    order_type = models.ForeignKey(
        MeasurementOrderDefinition,
        verbose_name='Based measurement order definition')
    measurement_items = models.ManyToManyField(MeasurementItem,
                                               verbose_name='Measured items')

    def __str__(self):
        items_str = ''
        for item in self.measurement_items.all():
            items_str += str(item) + ', '
        return self.order_type.name + ' ' + str(
            self.order_nr) + ' for ' + items_str

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.__str__() + '>'


def after_measurement_saved(instance, **kwargs):  # pylint: disable=W0613
    """
    Creates new CharacteristicValues after new Measurement was saved. Called
    via post_save signal
    """
    for value_type in instance.order_items.all():
        ch_value, _ = CharacteristicValue.objects.get_or_create(
            order=instance.order, value_type=value_type)
        ch_value.measurements.add(instance)
        ch_value.save()


def get_file_directory(_, filename):
    """
    Creates the path where the raw data file should be saved. The function is
    necessary to be able to change the path dynamic for the unit tests
    """
    name = os.path.split(filename)[-1]
    return os.path.join(settings.MEASUREMENT_FILE_DIR, name)


@python_2_unicode_compatible
class Measurement(models.Model):
    """
    Single measurement with raw and meta data
    """
    date = models.DateTimeField(verbose_name='Date of the measurement')
    order = models.ForeignKey(MeasurementOrder,
                              verbose_name='Measurement order')
    order_items = models.ManyToManyField(
        CharacteristicValueDefinition,
        verbose_name='Item of the measurement order')
    examiner = models.ForeignKey(User, verbose_name="Examiner")
    remarks = models.TextField(blank=True, verbose_name='Remarks')
    meas_item = models.ForeignKey(MeasurementItem,
                                  verbose_name='Measurement item')
    measurement_devices = models.ManyToManyField(
        MeasurementDevice, verbose_name='Used measurement devices')
    raw_data_file = models.FileField(verbose_name='Raw data file',
                                     upload_to=get_file_directory,
                                     max_length=500)
    measurement_tag = models.ForeignKey(
        MeasurementTag, blank=True, null=True,
        verbose_name="Tag to distinguish the Measurements")

    def __str__(self):
        return "Measurement from " + str(self.date)

    def get_absolute_url(self):
        """
        Returns the url of the measurement
        :return: Update-url
        """
        from django.core.urlresolvers import reverse
        return reverse('update_measurement', kwargs={'pk': self.pk})


post_save.connect(after_measurement_saved, sender=Measurement)


def after_charac_value_saved(instance, update_fields,
                             **kwargs):  # pylint: disable=W0613
    """
    Calculates the value of CharacteristicValues and updates the Plot sessions.
    Called via the post_saved signal
    """
    if not update_fields or 'measurements' in update_fields:
        _ = instance.value
        update_plot_sessions()


def save_position_in_cv(instance, update_fields, **kwargs):  # pylint: disable=W0613
    """
    Saves the position of the measurement in the CharacteristicValue
    """
    if not update_fields or 'measurements' in update_fields:
        if hasattr(instance, 'position'):
            from django.contrib.gis.geos import LineString
            points = []
            altitude = 0.0
            for meas in instance.measurements.all():
                points.append(meas.position)
                altitude += float(meas.altitude)
            if len(points) > 1:
                instance.position = LineString(points).centroid
            elif len(points) == 1:
                instance.position = points[0]
            count = instance.measurements.count()
            if count:
                instance.altitude = altitude / instance.measurements.count()
            instance.save(update_fields=['position', 'altitude'])


class CalcValueQuerySet(DataFrameQuerySet):
    """
    QuerySet for CharacteristicValues to enable lazy calculation. The value is
    only the first time or after the CalculationRule has changed.
    """
    value_re = recompile('^value([_]{2})')
    product_re = recompile('^product([_]{2})')
    MAX_NUM_CALCULATION = 2

    def __init__(self, *args, **kwargs):
        super(CalcValueQuerySet, self).__init__(*args, **kwargs)

    def count_unfinished(self):
        """
        :return: Returns the number of unfinished(not all necessary
         Measurements are available) CharacteristicValues
        """
        return self.filter(_finished=False).count()

    def count_invalid(self):
        """

        :return: Number of uncalculated CharacteristicValues
        """
        return self.filter(_is_valid=False, _finished=True).count()

    def filter_with_product(self, products, *args, **kwargs):
        """
        Filter CharacteristicValues for given product
        :param products: Single value or List of Products or Product ids
        :return: QuerySet of CharacteristicValues
        """
        if not hasattr(products, '__iter__'):
            products = [products]
        product_id = list()
        for prod in set(products):
            if isinstance(prod, Product):
                product_id.append(prod.pk)
            else:
                product_id.append(prod)
        product_q = Q(order__order_type__product=product_id[0])
        for pid in product_id[1:]:
            product_q |= Q(order__order_type__product=pid)
        return self.filter(product_q, *args, **kwargs)

    def filter(self, *args, **kwargs):
        """
        Overrides the filter method to enable lazy calculation
        """
        for query in args:
            if isinstance(query, Q):
                for index, exp in enumerate(query.children):
                    if isinstance(exp, tuple):
                        query.children[index] = (
                            self.value_re.sub(r'_calc_value\g<1>', exp[0]),
                            exp[1])
                        query.children[index] = (
                            self.product_re.sub(
                                r'order__order_type__product\g<1>',
                                exp[0]), exp[1])

        for key in kwargs:
            if key.startswith('value'):
                new_key = self.value_re.sub(r'_calc_value\g<1>', key)
                kwargs[new_key] = kwargs.pop(key)
            if key.startswith('product'):
                new_key = self.product_re.sub(
                    r'order__order_type__product\g<1>', key)
                kwargs[new_key] = kwargs.pop(key)
        return super(CalcValueQuerySet, self).filter(*args, **kwargs)

    def recalculation(self):
        """
        Calculates the value for invalid CharacteristicValues in the QuerySet
        """
        for value in self:
            _ = value.value

    def to_dataframe(self, fieldnames=(), verbose=True, index=None,
                     coerce_float=False):
        """
        Returns a DataFrame from the queryset, overrides the base method to
        enalbe lazy calculation


        :param fieldnames:  The model field names(columns) to utilise in
                     creating the DataFrame. You can span a relationships in
                     the usual Django ORM way by using the foreign key field
                     name separated by double underscores and refer to a field
                     in a related model.


        :param index:  specify the field to use  for the index. If the index
                field is not in fieldnames it will be appended. This
                is mandatory for timeseries.

        :param verbose: If  this is ``True`` then populate the DataFrame with
                the human readable versions for foreign key fields else
                use the actual values set in the model
        """
        if self.count_invalid() < self.MAX_NUM_CALCULATION:
            outdated_values = self.filter(_is_valid=False)
            outdated_values.recalculation()  # pylint: disable=E1101
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


CALC_VALUE_MANAGER = models.Manager.from_queryset(CalcValueQuerySet)   # pylint: disable=E1101


@python_2_unicode_compatible
class CharacteristicValue(models.Model):
    """
    Single characteristic value of an item (height, width, length etc.). The
    type is defined over the value_type (CharacteristicValue) which defines the
    name and how to calculate the value. The calculation of the value is lazy
    and is only done if the value is needed.
    CharacteristicValue is created automatically after a new Measurement is
    saved. It is possible that one Measurement creates many
    CharacteristicValues or that one CharacteristicValue needs many Measurement
    for the calculation.
    """
    order = models.ForeignKey(MeasurementOrder)
    value_type = models.ForeignKey(CharacteristicValueDefinition)
    measurements = models.ManyToManyField(Measurement)
    date = models.DateTimeField(auto_now_add=True)
    _is_valid = models.BooleanField(default=False)
    _finished = models.BooleanField(default=False)
    _calc_value = models.FloatField(blank=True, null=True)

    objects = CALC_VALUE_MANAGER()

    class Meta:
        unique_together = ['order', 'value_type']
        ordering = ['date']

    def __init__(self, *args, **kwargs):
        if 'order' in kwargs and 'value_type' in kwargs:
            order = kwargs['order']
            value_type = kwargs['value_type']
            if value_type not in order.order_type.characteristic_values.all():
                raise ValidationError(
                    'Characteristic Value is not demanded in order')
        super(CharacteristicValue, self).__init__(*args, **kwargs)

    @property
    def product(self):
        """
        Easy access to the product of the associated MeasurementItem
        """
        return self.order.order_type.product

    @property
    def value(self):
        """
        Value of the CharacteristicValue. If the value isn't calculated yet,
        it will be calculated
        """
        if self.is_valid and self._finished:
            return self._calc_value
        return self.__calculate_value()

    def __calculate_value(self):
        if self.measurements.count() < 1:
            return None
        calc_value = self.value_type.calculation_rule.calculate(
            self.measurements)
        self._is_valid = True
        if calc_value:
            self._calc_value = calc_value
            self._finished = True
            self.date = self.measurements.last().date
            self.save(force_insert=False, force_update=False, using=None,
                      update_fields=['_is_valid', '_calc_value',
                                     '_finished', 'date'])
        return self._calc_value

    def get_value_type_name(self):
        """
        Easy access to the name of the CharacteristicValueDefinition
        """
        return self.value_type.value_name

    @property
    def is_valid(self):
        """
        Is the value valid, or is a recalculation necessary
        """
        return self._is_valid

    @property
    def missing_keys(self):
        """
        Returns the name of MeasurementTags which are missing for the
        calculation
        """
        if self._finished:
            return set()
        rule = self.value_type.calculation_rule
        _ = rule.calculate(self.measurements)
        return rule.missing_keys

    def __str__(self):
        return str(self.order.order_nr) + ' ' + self.value_type.value_name

    def __repr__(self):
        return '<' + self.__class__.__name__ + \
               ': ' + self.value_type.value_name + ' >'


post_save.connect(after_charac_value_saved, sender=CharacteristicValue)
post_save.connect(save_position_in_cv, sender=CharacteristicValue)


@python_2_unicode_compatible  # pylint: disable=R0902
class PlotConfig(models.Model):
    """
    Configurtion of a plot which defines which data should be displayed and how
    """
    description = models.CharField(
        max_length=100, verbose_name='Description of the plotted data')
    short_name = models.URLField(
        verbose_name='Short name of configuration. Also used for url',
        unique=True)
    histogram = models.BooleanField(verbose_name='Show histogram',
                                    default=True)
    _titles = models.TextField(verbose_name='Title of the plots', default='')
    _filter_args = models.BinaryField(
        blank=True,
        verbose_name='Pickled list of dictionaries with filter lookup strings')
    _plot_args = models.BinaryField(
        blank=True,
        verbose_name='Pickle of List of dictionaries with plot parameter')
    _annotations = models.BinaryField(
        blank=True, verbose_name='Plot annotations which should be shown')

    def __init__(self, *args, **kwargs):
        super(PlotConfig, self).__init__(*args, **kwargs)

        self.__last_filter_args = None
        self.__last_plot_args = None
        self.__last_annotations = None

    @property
    def titles(self):
        """
        List of Titles of the plot
        """
        num_filter = len(self.filter_args)
        titles = self._titles.split('|')
        _ = [titles.append('') for _ in range(num_filter - len(titles))]
        if len(titles) > num_filter:
            titles = titles[:num_filter]
        return titles

    @titles.setter
    def titles(self, value):
        """
        Sets the title of the plots
        :param value: String or list of strings with the title of the plots
        :return:
        """
        if isinstance(value, list):
            num_filter = len(self.filter_args)
            if len(value) > num_filter:
                value = value[:num_filter]
            value = '|'.join(value)
        self._titles = value

    @property
    def filter_args(self):
        """
        Returns dictionary with the filter arguments to get plot data. The
        dictionary is saved in the database as pickle
        """
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
        """
        Returns dictionary with the plot arguments for the plot (color, line
        style etc). The dictionary is saved in the database as pickle
        """
        if not self._plot_args:
            return []
        if not self.__last_plot_args:
            self.__last_plot_args = pickle.loads(self._plot_args)
        return self.__last_plot_args

    @plot_args.setter
    def plot_args(self, plot_args):
        self.__last_plot_args = plot_args
        self._plot_args = pickle.dumps(plot_args)

    @property
    def annotations(self):
        """
        Annotations (Control limits, Mean etc) which should be displayed in the
        plot. The list is saved in the database as pickle
        """
        if not self._annotations:
            return []
        if not self.__last_annotations:
            self.__last_annotations = pickle.loads(self._annotations)
        return self.__last_annotations

    @annotations.setter
    def annotations(self, annotations_dict):
        self.__last_annotations = annotations_dict
        self._annotations = pickle.dumps(annotations_dict)

    def get_annotation_container(self):
        """
        Returns a Container with all annotations which will be displayed in the
        plot
        """
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

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        if self.filter_args:
            plot_args = self.plot_args
            annotations = self.annotations
            max_list = len(self.filter_args)
            for _ in range(max_list - len(plot_args)):
                plot_args.append({})
            for _ in range(max_list - len(annotations)):
                annotations.append({})
            self.plot_args = plot_args
            self.annotations = annotations
        super(PlotConfig, self).save(force_insert, force_update, using,
                                     update_fields)

    def __str__(self):
        return str(self.short_name)

    def __repr__(self):
        return '<' + self.__class__.__name__ + ': ' + self.short_name + ' >'


class UserPlotSession(models.Model):
    """
    Currently connected browser bokeh plot session
    """
    bokeh_session_id = models.CharField(max_length=64)
    plot_config = models.ForeignKey(PlotConfig,
                                    verbose_name="Plot configuration")
    index = models.IntegerField(verbose_name='Index of plot configuration',
                                default=0)
