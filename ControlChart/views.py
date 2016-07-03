#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Views for the  ControlChart app
"""
import json
from collections import defaultdict

from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.urlresolvers import reverse_lazy
from django.forms import ModelForm, Select, SplitDateTimeField
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.utils.timezone import now
from django.views.generic import CreateView, ListView, UpdateView
from django.views.generic import DeleteView, TemplateView

from ControlChart.plot_util import PlotGenerator, update_plot_sessions
from .forms import NewMeasurementItemForm, NewMeasurementOrderForm
from .models import CharacteristicValueDefinition, PlotConfig, Product
from .models import Measurement, MeasurementOrder, CalculationRule
from .models import MeasurementDevice
from .models import MeasurementItem, MeasurementOrderDefinition
from .models import MeasurementTag, CharacteristicValue, CalcValueQuerySet
from .multiform import MultiFormsView


class AddContextInfoMixIn(object):  # pylint: disable=R0903
    """
    Mixin to add additional information to the context
    """
    def get_context_data(self, **kwargs):
        """
        Add additional information to the context
         * current_path: base url
         * class_name: Name of the model class
         * add_class: Add permission name for the model class
         * change_class: Change permission name for the model class
         * delete_class: Delete permission name for the model class
         * verbose_field_names: Verbose field names of the model
        """
        # pylint: disable=W0212
        context = super(AddContextInfoMixIn, self).get_context_data(**kwargs)
        context['current_path'] = self.request.META['PATH_INFO']
        context['class_name'] = self.model._meta.model_name
        context['add_class'] = self.model._meta.app_label + '.add_' + \
                               self.model._meta.model_name
        context['change_class'] = self.model._meta.app_label + '.change_' + \
                                  self.model._meta.model_name
        context['delete_class'] = self.model._meta.app_label + '.delete_' + \
                                  self.model._meta.model_name
        if hasattr(self, 'fields') and self.fields:
            verbose_field_names = []
            for field_name in self.fields:
                field = self.model._meta.get_field_by_name(field_name)[0]
                verbose_field_names.append(field.verbose_name)
            context['verbose_field_names'] = verbose_field_names
        # pylint: enable=W0212
        return context


class TitledListView(AddContextInfoMixIn, ListView):  # pylint: disable=R0901
    """
    Base class for a ListView with title and additional context data
    """
    title = None
    model_name = None
    list_link_name = None
    paginate_by = 20

    def __init__(self, title=None, model_name=None, list_link_name=None,
                 *args, **kwargs):
        self.title = title
        self.model_name = model_name
        self.list_link_name = list_link_name
        super(TitledListView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Adds title, model name and urls to this list view to the context data
        """
        context = super(TitledListView, self).get_context_data(**kwargs)
        # pylint: disable=W0212
        if not self.title:
            self.title = 'List of ' + str(self.model._meta.verbose_name_plural)
        if not self.model_name:
            self.model_name = str(self.model._meta.verbose_name_plural)
        if not self.list_link_name:
            self.list_link_name = '_'.join(
                str(self.model._meta.verbose_name).split())
        # pylint: enable=W0212
        context['title'] = self.title
        context['model_name'] = self.model_name
        context['list_link_name'] = self.list_link_name
        return context


class NewCharacteristicValueDefinition(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create new CharacteristicValueDefinitions
    """
    template_name = "new_base.html"
    model = CharacteristicValueDefinition
    fields = ['value_name', 'description', 'calculation_rule',
              'possible_meas_devices']
    success_url = '/'


class ListCharacteristicValueDefinition(TitledListView):  # pylint: disable=R0901
    """
    View to list all CharacteristicValueDefinitions
    """
    template_name = "list_characteristic_value_definition.html"
    model = CharacteristicValueDefinition
    fields = ['value_name', 'description']


class UpdateCharacteristicValueDefinition(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a CharacteristicValueDefinition
    """
    template_name = "new_base.html"
    model = CharacteristicValueDefinition
    fields = ['value_name', 'description', 'calculation_rule',
              'possible_meas_devices']
    success_url = '/'


class DeleteCharacteristicValueDefinition(DeleteView):  # pylint: disable=R0901
    """
    View to delete a CharacteristicValueDefiniton
    """
    template_name = "delete_base.html"
    model = CharacteristicValueDefinition
    success_url = reverse_lazy('list_characteristic_value_definition')


class NewMeasurementDevice(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new MeasurementDevice
    """
    template_name = "new_base.html"
    model = MeasurementDevice
    fields = ['name', 'serial_nr']
    success_url = '/'


class ListMeasurementDevice(TitledListView):  # pylint: disable=R0901
    """
    View to list all MeasurementDevices
    """
    template_name = "list_measurement_device.html"
    model = MeasurementDevice
    fields = ['name', 'serial_nr']


class UpdateMeasurementDevice(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a MeasurementDevice
    """
    template_name = "new_base.html"
    model = MeasurementDevice
    fields = ['name', 'serial_nr']
    success_url = '/'


class DeleteMeasurementDevice(DeleteView):  # pylint: disable=R0901
    """
    View to delete a MeasurementDevice
    """
    template_name = "delete_base.html"
    model = MeasurementDevice
    success_url = reverse_lazy('list_measurement_device')


class NewMeasurementOrder(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new MeasuremetOrder
    """
    template_name = "new_base.html"
    model = MeasurementOrder
    fields = ['order_type', 'measurement_items']
    success_url = '/'


class ListMeasurementOrder(TitledListView):  # pylint: disable=R0901
    """
    View to list all MeasurementOrders
    """
    template_name = "list_measurement_order.html"
    model = MeasurementOrder
    fields = ['order_nr', 'order_type', 'measurement_items']


class UpdateMeasurementOrder(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a MeasurementOrder
    """
    template_name = "new_base.html"
    model = MeasurementOrder
    fields = ['order_nr', 'order_type', 'measurement_items']
    success_url = '/'


class DeleteMeasurementOrder(DeleteView):  # pylint: disable=R0901
    """
    View to delete a MeasurementOrder
    """
    template_name = "delete_base.html"
    model = MeasurementOrder
    success_url = reverse_lazy('list_measurement_order')


class NewMeasurementOrderDefinition(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new MeasurementOrderDefinition
    """
    template_name = "new_base.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values', 'product']
    success_url = '/'


class ListMeasurementOrderDefinition(TitledListView):  # pylint: disable=R0901
    """
    View to list all MeasurementOrderDefinitions
    """
    template_name = "list_measurement_order_definition.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values', 'product']


class UpdateMeasurementOrderDefinition(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a MeasurementOrderDefinition
    """
    template_name = "new_base.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values', 'product']
    success_url = '/'


class DeleteMeasurementOrderDefinition(DeleteView):  # pylint: disable=R0901
    """
    View to delete a MeasurementOrderDefinition
    """
    template_name = "delete_base.html"
    model = MeasurementOrderDefinition
    success_url = reverse_lazy('list_measurement_order_definition')


class NewMeasurementItem(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new MeasurementItem
    """
    template_name = "new_base.html"
    model = MeasurementItem
    fields = ['serial_nr', 'name', 'product']
    success_url = '/'


class ListMeasurementItem(TitledListView):  # pylint: disable=R0901
    """
    View to list all MeasurementItem
    """
    template_name = "list_measurement_item.html"
    model = MeasurementItem
    fields = ['serial_nr', 'name', 'product']


class UpdateMeasurementItem(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a MeasurementItem
    """
    template_name = "new_base.html"
    model = MeasurementItem
    fields = ['serial_nr', 'name', 'product']
    success_url = '/'


class DeleteMeasurementItem(DeleteView):  # pylint: disable=R0901
    """
    View to delete a MeasurementItem
    """
    template_name = "delete_base.html"
    model = MeasurementItem
    success_url = reverse_lazy('list_measurement_item')


class NewCalculationRule(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new CalculationRule
    """
    template_name = "new_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name', 'rule_code']
    success_url = '/'


class ListCalculationRule(TitledListView):  # pylint: disable=R0901
    """
    View to list all CalculationRule
    """
    template_name = "list_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name']


class UpdateCalculationRule(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a CalculationRule
    """
    template_name = "new_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name', 'rule_code']
    success_url = '/'


class DeleteCalculationRule(DeleteView):  # pylint: disable=R0901
    """
    View to delete a CalculationRule
    """
    template_name = "delete_base.html"
    model = CalculationRule
    success_url = reverse_lazy('list_calculation_rule')


class NewMeasurementTag(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new MeasurementTag
    """
    template_name = "new_base.html"
    model = MeasurementTag
    fields = ['name']
    success_url = "/"


class ListMeasurementTag(TitledListView):  # pylint: disable=R0901
    """
    View to list all MeasurementTag
    """
    template_name = "list_measurement_tag.html"
    model = MeasurementTag
    fields = ['name']


class UpdateMeasurementTag(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a MeasurementTag
    """
    template_name = "new_base.html"
    model = MeasurementTag
    fields = ['name']
    success_url = '/'


class DeleteMeasurementTag(DeleteView):  # pylint: disable=R0901
    """
    View to delete a MeasurementTag
    """
    template_name = "delete_base.html"
    model = MeasurementTag
    success_url = reverse_lazy('list_measurement_tag')


class NewProduct(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new Product
    """
    template_name = "new_base.html"
    model = Product
    fields = ['product_name']
    success_url = "/"


class ListProduct(TitledListView):  # pylint: disable=R0901
    """
    View to list all Product
    """
    template_name = "list_product.html"
    model = Product
    fields = ['product_name']


class UpdateProduct(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a Product
    """
    template_name = "new_base.html"
    model = Product
    fields = ['product_name']
    success_url = '/'


class DeleteProduct(DeleteView):  # pylint: disable=R0901
    """
    View to delete a Product
    """
    template_name = "delete_base.html"
    model = Product
    success_url = reverse_lazy('list_product')


class MeasurementFrom(ModelForm):
    """
    Form class for creating an editing a measurement model instance.
    Uses the AdminSplitDateTime widget for the DateTimeField
    """

    class Meta:
        model = Measurement
        fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
                  'meas_item', 'measurement_devices', 'raw_data_file',
                  'measurement_tag']
        field_classes = {
            'date': SplitDateTimeField
        }
        widgets = {
            'date': AdminSplitDateTime(),
            'order': Select(attrs={'onchange': 'get_order_items();'})
        }


class NewMeasurement(AddContextInfoMixIn, CreateView):  # pylint: disable=R0901
    """
    View to create a new Measurement
    """
    template_name = "new_measurement.html"
    form_class = MeasurementFrom
    model = Measurement
    success_url = "/"

    def get_initial(self):
        return {'date': now(), 'examiner': self.request.user}

    def post(self, request, *args, **kwargs):
        if request.is_ajax and 'check' in request.POST:
            cv_exits = False
            update_url = ''
            for val_type in request.POST.getlist('order_items[]'):
                cvs = CharacteristicValue.objects.filter(
                    order=request.POST['order'], value_type=val_type)
                if cvs.exists():
                    cv_exits = True
                    first_measurement = cvs.first().measurements.first()
                    update_url = first_measurement.get_absolute_url()
            return JsonResponse({'exists': cv_exits, 'update_url': update_url})

        response = super(NewMeasurement, self).post(request, *args, **kwargs)
        if self.object:
            self.object.save()
        return response


class ListMeasurement(TitledListView):  # pylint: disable=R0901
    """
    View to list all Measurement
    """
    template_name = "list_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'meas_item',
              'measurement_tag']


class UpdateMeasurement(AddContextInfoMixIn, UpdateView):  # pylint: disable=R0901
    """
    View to update a Measurement
    """
    template_name = "new_measurement.html"
    model = Measurement
    form_class = MeasurementFrom
    success_url = '/'


class DeleteMeasurement(DeleteView):  # pylint: disable=R0901
    """
    View to delete a Measurement
    """
    template_name = "delete_base.html"
    model = Measurement
    success_url = reverse_lazy('list_measurement')


class ListPlotConfig(TitledListView):  # pylint: disable=R0901
    """
    View to list all PlotConfig
    """
    template_name = "list_plot_configuration.html"
    model = PlotConfig
    fields = ['description', 'short_name']


class DeletePlotConfig(DeleteView):  # pylint: disable=R0901
    """
    View to delete a PlotConfig
    """
    template_name = "delete_base.html"
    model = PlotConfig
    success_url = reverse_lazy('list_plot_configuration')


class NewMeasurementItemAndOrder(MultiFormsView):
    """
    View to create a new MeasurementOrder with MeasurementItems in one form
    """
    template_name = 'new_item_and_order.html'
    form_classes = {'item': NewMeasurementItemForm,
                    'order': NewMeasurementOrderForm}
    success_url = '/'

    def forms_valid(self, forms, form_name=''):
        items = []
        form = forms['item']
        for serial_nr, name, product_id in zip(form.data.getlist('serial_nr'),
                                               form.data.getlist('name'),
                                               form.data.getlist('product')):
            product = Product.objects.get(id=product_id)
            items.append(
                MeasurementItem.objects.get_or_create(serial_nr=serial_nr,
                                                      name=name,
                                                      product=product)[0])
        order_type = MeasurementOrderDefinition.objects.get(
            pk=int(forms['order'].data['order_type']))
        order = MeasurementOrder.objects.create(order_type=order_type)
        for item in items:
            order.measurement_items.add(item)
        order.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        forms['serial_nrs'] = forms['item'].data.getlist('serial_nr')
        forms['names'] = forms['item'].data.getlist('name')
        forms['products'] = forms['item'].data.getlist('product')
        return self.render_to_response(self.get_context_data(forms=forms))


def get_ajax_order_info(request):
    """
    Ajax request to get detail information about the measurement order for auto
    filling the new measurement form
    """
    start_tuple = (-1, 'Please select first the order')
    items_response = {'order_items': [start_tuple],
                      'meas_devices': [start_tuple],
                      'meas_items': [start_tuple]}
    if request.is_ajax() and request.method == 'POST' and request.POST['order']:
        order_items_response = []
        meas_devices_response = []
        meas_item_response = []
        order_pk = int(request.POST['order'])
        order = MeasurementOrder.objects.get(pk=order_pk)
        order_items = order.order_type.characteristic_values.all()
        meas_items = order.measurement_items.all()
        for item in order_items:
            devices = item.possible_meas_devices.all()
            for dev in devices:
                meas_devices_response.append((dev.pk, str(dev)))
            meas_devices_response = sorted(set(meas_devices_response))
            order_items_response.append((item.pk, item.description))
        for item in meas_items:
            meas_item_response.append((item.pk, str(item)))
        meas_item_response = sorted(set(meas_item_response))
        return JsonResponse({'order_items': order_items_response,
                             'meas_devices': meas_devices_response,
                             'meas_items': meas_item_response}, )
    return JsonResponse(items_response)


def get_ajax_meas_item(request):
    """
    Ajax request to get data for autocomplete of the MeasurementItem
    """
    response = {'suggestions': []}
    if request.is_ajax() and request.method == 'POST' and \
            request.POST['serial_nr']:
        serial_nr = request.POST['serial_nr']
        items = MeasurementItem.objects.filter(serial_nr__istartswith=serial_nr)
        serial_nr_response = []
        name_response = []
        product_response = []

        for item in items:
            response['suggestions'].append(
                {'value': item.serial_nr, 'data': (item.name, item.product.pk)})
            serial_nr_response.append(item.serial_nr)
            name_response.append(item.name)
            product_response.append(item.product.pk)
    return JsonResponse(response)


def recalc_characteristic_values(_):
    """
    View to calculate all invalid CharacteristicValues
    """
    context = dict()
    context['num_of_invalid'] = CharacteristicValue.objects.count_invalid()
    unfinished_values = CharacteristicValue.objects.filter(_finished=False)
    context['num_not_finished'] = unfinished_values.count()
    missing_keys = {}
    for cvalue in unfinished_values:
        missing_keys[str(cvalue)] = ','.join(cvalue.missing_keys)
    context['missing_keys'] = missing_keys
    return render_to_response('recalc_view.html', context)


def recalculate_invalid(request):
    """
    Ajax request to get the number of invalid CharacteristicValue.
    """
    if request.is_ajax() and request.method == 'POST':
        invalid_values = __get_invalid_values(request)
        for val in invalid_values:
            _ = val.value
    return JsonResponse({})


def __get_invalid_values(request):
    if 'filter_args' in request.POST:
        filter_args = json.loads(request.POST['filter_args'])
        invalid_values = CharacteristicValue.objects.filter(_finished=True,
                                                            **filter_args)
    else:
        invalid_values = CharacteristicValue.objects.filter(_is_valid=False,
                                                            _finished=True)
    return invalid_values


def recalculate_progress(request):
    """
    Ajax request to get the progress of the calculation
    """
    if request.is_ajax() and request.method == 'POST' and \
            request.POST['start_num']:
        num_invalid_val = __get_invalid_values(request).count_invalid()
        start_num = int(request.POST['start_num'])
        progress = int((start_num - num_invalid_val) * 100.0 / start_num)
        finished = num_invalid_val == 0
        if finished:
            update_plot_sessions()
        return JsonResponse(
            {'progress': str(progress), 'remaining': str(num_invalid_val),
             'finished': finished})
    return JsonResponse({'progress': '0', 'remaining': '0', 'finished': True})


def plot_given_configuration(request, configuration, index=None):
    """
    View the plots for given configurations.
    """
    context = defaultdict(list)
    try:
        plot_config = PlotConfig.objects.get(short_name=configuration)
        plot_generator = PlotGenerator(plot_config, index=index)

        counter = 0
        for script, num_invalid in plot_generator.plot_code_iterator():
            context['script_list'].append(script)
            context['recalc_needed_list'].append(
                num_invalid > CalcValueQuerySet.MAX_NUM_CALCULATION)
            context['filter_args_list'].append(
                json.dumps(plot_config.filter_args[counter]))
            context['num_of_invalid_list'].append(num_invalid)
            context['summary_list'].append(
                plot_generator.summary_for_last_plot())

            counter += 1
        context['content_values'] = zip(context['script_list'],
                                        context['recalc_needed_list'],
                                        context['num_of_invalid_list'],
                                        context['summary_list'],
                                        plot_config.titles)
        context['script_values'] = zip(context['recalc_needed_list'],
                                       context['filter_args_list'],
                                       context['num_of_invalid_list'])
        context['current_path'] = request.path
        if index is not None:
            context['is_detail_view'] = True
            context['values'] = plot_generator.values_for_last_plot()[
                ['date', 'measurements__meas_item__serial_nr',
                 'measurements__examiner', '_calc_value',
                 'id']].values
    except PlotConfig.DoesNotExist:
        raise Http404
    return render_to_response('plot_page.html', context=context)


class Dashboard(TemplateView):
    """
    Dashboard page to welcome the user.
    """
    template_name = 'dashboard.html'

    def __init__(self, **kwargs):
        super(Dashboard, self).__init__(**kwargs)
        self.last_changed_products = list()

    def get(self, request, *args, **kwargs):
        self.last_changed_products = list()
        for cvalue in CharacteristicValue.objects.all().order_by('-date'):
            if cvalue.product not in self.last_changed_products:
                self.last_changed_products.append(cvalue.product)
                if len(self.last_changed_products) > 3:
                    break
        return super(Dashboard, self).get(request, *args, **kwargs)
