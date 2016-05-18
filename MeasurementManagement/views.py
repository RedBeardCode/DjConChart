# Create your views here.
import json
from collections import defaultdict
from datetime import datetime

from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.urlresolvers import reverse_lazy
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from MeasurementManagement.plot_util import PlotGenerator, update_plot_sessions
from .forms import NewMeasurementItemForm, NewMeasurementOrderForm
from .models import CharacteristicValueDescription, PlotConfig, CalcValueQuerySet
from .models import Measurement, MeasurementOrder, CalculationRule, MeasurementTag, CharacteristicValue, Product
from .models import MeasurementItem, MeasurementOrderDefinition, MeasurementDevice
from .multiform import MultiFormsView


class AddContextInfoMixIn(object):
    def get_context_data(self, **kwargs):
        context = super(AddContextInfoMixIn, self).get_context_data(**kwargs)
        context['current_path'] = self.request.META['PATH_INFO']
        context['class_name'] = self.model._meta.model_name
        context['add_class'] = self.model._meta.app_label + '.add_' + self.model._meta.model_name
        context['change_class'] = self.model._meta.app_label + '.change_' + self.model._meta.model_name
        context['delete_class'] = self.model._meta.app_label + '.delete_' + self.model._meta.model_name
        if hasattr(self, 'fields') and self.fields:
            verbose_field_names = []
            for field_name in self.fields:
                field = self.model._meta.get_field_by_name(field_name)[0]
                verbose_field_names.append(field.verbose_name)
            context['verbose_field_names'] = verbose_field_names
        return context

class TitledListView(AddContextInfoMixIn, ListView):
    title = None
    model_name = None
    list_link_name = None
    paginate_by = 20

    def __init__(self, *args, title=None, model_name=None, list_link_name=None, **kwargs):
        super(TitledListView, self).__init__(*args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(TitledListView, self).get_context_data(**kwargs)
        if not self.title:
            self.title = 'List of ' + str(self.model._meta.verbose_name_plural)
        if not self.model_name:
            self.model_name = str(self.model._meta.verbose_name_plural)
        if not self.list_link_name:
            self.list_link_name = '_'.join(str(self.model._meta.verbose_name).split())
        context['title'] = self.title
        context['model_name'] = self.model_name
        context['list_link_name'] = self.list_link_name
        return context


class NewCharacteristicValueDescription(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = CharacteristicValueDescription
    fields = ['value_name', 'description', 'calculation_rule', 'possible_meas_devices']
    success_url = '/'


class ListCharacteristicValueDescription(TitledListView):
    template_name = "list_characteristic_value_description.html"
    model = CharacteristicValueDescription
    fields = ['value_name', 'description']


class UpdateCharacteristicValueDescription(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = CharacteristicValueDescription
    fields = ['value_name', 'description', 'calculation_rule', 'possible_meas_devices']
    success_url = '/'


class DeleteCharacteristicValueDescription(DeleteView):
    template_name = "delete_base.html"
    model = CharacteristicValueDescription
    success_url = reverse_lazy('list_characteristic_value_description')


class NewMeasurementDevice(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementDevice
    fields = ['name', 'sn']
    success_url = '/'


class ListMeasurementDevice(TitledListView):
    template_name = "list_measurement_device.html"
    model = MeasurementDevice
    fields = ['name', 'sn']


class UpdateMeasurementDevice(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = MeasurementDevice
    fields = ['name', 'sn']
    success_url = '/'


class DeleteMeasurementDevice(DeleteView):
    template_name = "delete_base.html"
    model = MeasurementDevice
    success_url = reverse_lazy('list_measurement_device')


class NewMeasurementOrder(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementOrder
    fields = ['order_type', 'measurement_items']
    success_url = '/'


class ListMeasurementOrder(TitledListView):
    template_name = "list_measurement_order.html"
    model = MeasurementOrder
    fields = ['order_nr', 'order_type', 'measurement_items']


class UpdateMeasurementOrder(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = MeasurementOrder
    fields = ['order_nr', 'order_type', 'measurement_items']
    success_url = '/'


class DeleteMeasurementOrder(DeleteView):
    template_name = "delete_base.html"
    model = MeasurementOrder
    success_url = reverse_lazy('list_measurement_order')


class NewMeasurementOrderDefinition(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values', 'product']
    success_url = '/'


class ListMeasurementOrderDefinition(TitledListView):
    template_name = "list_measurement_order_definition.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values', 'product']


class UpdateMeasurementOrderDefinition(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values', 'product']
    success_url = '/'


class DeleteMeasurementOrderDefinition(DeleteView):
    template_name = "delete_base.html"
    model = MeasurementOrderDefinition
    success_url = reverse_lazy('list_measurement_order_definition')


class NewMeasurementItem(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementItem
    fields = ['sn', 'name', 'product']
    success_url = '/'


class ListMeasurementItem(TitledListView):
    template_name = "list_measurement_item.html"
    model = MeasurementItem
    fields = ['sn', 'name', 'product']


class UpdateMeasurementItem(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = MeasurementItem
    fields = ['sn', 'name', 'product']
    success_url = '/'


class DeleteMeasurementItem(DeleteView):
    template_name = "delete_base.html"
    model = MeasurementItem
    success_url = reverse_lazy('list_measurement_item')


class NewCalculationRule(AddContextInfoMixIn, CreateView):
    template_name = "new_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name', 'rule_code']
    success_url = '/'


class ListCalculationRule(TitledListView):
    template_name = "list_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name']


class UpdateCalculationRule(AddContextInfoMixIn, UpdateView):
    template_name = "new_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name', 'rule_code']
    success_url = '/'


class DeleteCalculationRule(DeleteView):
    template_name = "delete_base.html"
    model = CalculationRule
    success_url = reverse_lazy('list_calculation_rule')


class NewMeasurementTag(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementTag
    fields = ['name']
    success_url = "/"


class ListMeasurementTag(TitledListView):
    template_name = "list_measurement_tag.html"
    model = MeasurementTag
    fields = ['name']


class UpdateMeasurementTag(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = MeasurementTag
    fields = ['name']
    success_url = '/'


class DeleteMeasurementTag(DeleteView):
    template_name = "delete_base.html"
    model = MeasurementTag
    success_url = reverse_lazy('list_measurement_tag')


class NewProduct(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = Product
    fields = ['product_name']
    success_url = "/"


class ListProduct(TitledListView):
    template_name = "list_product.html"
    model = Product
    fields = ['product_name']


class UpdateProduct(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = Product
    fields = ['product_name']
    success_url = '/'


class DeleteProduct(DeleteView):
    template_name = "delete_base.html"
    model = Product
    success_url = reverse_lazy('list_product')


class MeasurementFormMixin(object):

    def get_form(self, form_class=None):
        form = super(MeasurementFormMixin, self).get_form(form_class)
        field = form.fields['date']
        field.initial = datetime.now()
        field.widget = AdminSplitDateTime()
        form.fields['date'] = field
        form.fields['order'].widget.attrs.update({'onchange': 'get_order_items();'})
        form.fields['examiner'].initial = self.request.user
        return form


class NewMeasurement(MeasurementFormMixin, AddContextInfoMixIn, CreateView):
    template_name = "new_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
              'meas_item', 'measurement_devices', 'raw_data_file', 'measurement_tag']
    success_url = "/"

    def post(self, request, *args, **kwargs):
        if request.is_ajax and 'check' in request.POST:
            cv_exits = False
            update_url = ''
            for val_type in request.POST.getlist('order_items[]'):
                cvs = CharacteristicValue.objects.filter(order=request.POST['order'], value_type=val_type)
                if cvs.exists():
                    cv_exits = True
                    update_url = cvs.first().measurements.first().get_absolute_url()
            return JsonResponse({'exists': cv_exits, 'update_url': update_url})

        response = super(NewMeasurement, self).post(request, *args, **kwargs)
        if self.object:
            self.object.save()
        return response

class ListMeasurement(TitledListView):
    template_name = "list_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'meas_item', 'measurement_tag']


class UpdateMeasurement(MeasurementFormMixin, AddContextInfoMixIn, UpdateView):
    template_name = "new_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
              'meas_item', 'measurement_devices', 'raw_data_file', 'measurement_tag']
    success_url = '/'


class DeleteMeasurement(DeleteView):
    template_name = "delete_base.html"
    model = Measurement
    success_url = reverse_lazy('list_measurement')



class NewMeasurementItemAndOrder(MultiFormsView):
    template_name = 'new_item_and_order.html'
    form_classes = {'item': NewMeasurementItemForm,
                    'order': NewMeasurementOrderForm}
    success_url = '/'

    def forms_valid(self, forms, form_name=''):
        items = []
        form = forms['item']
        for sn, name, product_id in zip(form.data.getlist('sn'),
                                        form.data.getlist('name'),
                                        form.data.getlist('product')):
            product = Product.objects.get(id=product_id)
            items.append(MeasurementItem.objects.get_or_create(sn=sn, name=name, product=product)[0])
        order_type = MeasurementOrderDefinition.objects.get(pk=int(forms['order'].data['order_type']))
        order = MeasurementOrder.objects.create(order_type=order_type)
        for item in items:
            order.measurement_items.add(item)
        order.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        forms['sns'] = forms['item'].data.getlist('sn')
        forms['names'] = forms['item'].data.getlist('name')
        forms['products'] = forms['item'].data.getlist('product')
        return self.render_to_response(self.get_context_data(forms=forms))


def get_ajax_order_info(request):
    start_tuple = (-1, 'Please select first the order')
    items_response = {'order_items': [start_tuple], 'meas_devices': [start_tuple], 'meas_items': [start_tuple]}
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
        return JsonResponse({'order_items': order_items_response, 'meas_devices': meas_devices_response,
                             'meas_items': meas_item_response}, )
    return JsonResponse(items_response)


def get_ajax_meas_item(request):
    response = {'suggestions': []}
    if request.is_ajax() and request.method == 'POST' and request.POST['sn']:
        sn = request.POST['sn']
        items = MeasurementItem.objects.filter(sn__istartswith=sn)
        sn_response = []
        name_response = []

        for item in items:
            response['suggestions'].append({'value': item.sn, 'data': item.name})
            sn_response.append(item.sn)
            name_response.append(item.name)

    return JsonResponse(response)


def recalc_characteristic_values(request, type=''):
    context = {}
    context['num_of_invalid'] = CharacteristicValue.objects.count_invalid()
    unfinished_values = CharacteristicValue.objects.filter(_finished=False)
    context['num_not_finished'] = unfinished_values.count()
    missing_keys = {}
    for cv in unfinished_values:
        missing_keys[str(cv)] = ','.join(cv.missing_keys)
    context['missing_keys'] = missing_keys
    return render_to_response('recalc_view.html', context)


def recalculate_invalid(request):
    if request.is_ajax() and request.method == 'POST':
        invalid_values = __get_invalid_values(request)
        for val in invalid_values:
            dummy = val.value
    return JsonResponse({})


def __get_invalid_values(request):
    if 'filter_args' in request.POST:
        filter_args = json.loads(request.POST['filter_args'])
        invalid_values = CharacteristicValue.objects.filter(_finished=True, **filter_args)
    else:
        invalid_values = CharacteristicValue.objects.filter(_is_valid=False, _finished=True)
    return invalid_values


def recalculate_progress(request):
    if request.is_ajax() and request.method == 'POST' and request.POST['start_num']:
        num_invalid_val = __get_invalid_values(request).count_invalid()
        start_num = int(request.POST['start_num'])
        progress = int((start_num - num_invalid_val) * 100.0 / start_num)
        finished = num_invalid_val == 0
        if finished:
            update_plot_sessions()
        return JsonResponse(
            {'progress': str(progress), 'remaining': str(num_invalid_val), 'finished': finished})
    return JsonResponse({'progress': '0', 'remaining': '0', 'finished': True})


def plot_given_configuration(request, configuration, index=None):
    context = defaultdict(list)
    try:
        plot_config = PlotConfig.objects.get(short_name=configuration)
        plot_generator = PlotGenerator(plot_config, index=index)

        counter = 0
        for script, num_invalid in plot_generator.create_plot_code_iterator():
            context['script_list'].append(script)
            context['recalc_needed_list'].append(num_invalid > CalcValueQuerySet.MAX_NUM_CALCULATION)
            context['filter_args_list'].append(json.dumps(plot_config.filter_args[counter]))
            context['num_of_invalid_list'].append(num_invalid)
            counter += 1
        context['content_values'] = zip(context['script_list'], context['recalc_needed_list'],
                                        context['num_of_invalid_list'])
        context['script_values'] = zip(context['recalc_needed_list'], context['filter_args_list'],
                                       context['num_of_invalid_list'])
        context['current_path'] = request.path
    except PlotConfig.DoesNotExist:
        raise Http404
    return render_to_response('single_plot.html', context=context)

