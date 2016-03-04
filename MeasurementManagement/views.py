# Create your views here.
from datetime import datetime
from math import pi

from bokeh.models import FactorRange
from django.views.generic import CreateView
from django.contrib.admin.widgets import AdminSplitDateTime
from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from bokeh.plotting import figure, curdoc
from bokeh.client import push_session
from bokeh.embed import autoload_server

from MeasurementManagement.plot_annotation import PlotAnnotationContainer, FixedMaxAnnotation, FixedMinAnnotation
from .models import Measurement, MeasurementOrder, CalculationRule, MeasurementTag, CharacteristicValue
from .models import MeasurementItem, MeasurementOrderDefinition, MeasurementDevice
from .models import CharacteristicValueDescription
from .multiform import MultiFormsView
from .forms import NewMeasurementItemForm, NewMeasurementOrderForm


class NewCharacteristicValueDescription(CreateView):
    template_name = "new_base.html"
    model = CharacteristicValueDescription
    fields = ['value_name', 'description', 'calculation_rule', 'possible_meas_devices']
    success_url = '/'

class NewMeasurementDevice(CreateView):
    template_name = "new_base.html"
    model = MeasurementDevice
    fields = ['name', 'sn']
    success_url = '/'

class NewMeasurementOrder(CreateView):
    template_name = "new_measurement_order.html"
    model = MeasurementOrder
    fields = ['order_type', 'measurement_items']
    success_url = '/'



class NewMeasurementOrderDefinition(CreateView):
    template_name = "new_base.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values']
    success_url = '/'

class NewMeasurementItem(CreateView):
    template_name = "new_base.html"
    model = MeasurementItem
    fields = ['sn', 'name']
    success_url = '/'

class NewCalculationRule(CreateView):
    template_name = "new_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name', 'rule_code']
    success_url = '/'


class NewMeasurementTag(CreateView):
    template_name = "new_base.html"
    model = MeasurementTag
    fields = ['name']
    success_url = "/"

class NewMeasurement(CreateView):
    template_name = "new_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
              'meas_item', 'measurement_devices', 'raw_data_file', 'measurement_tag']
    success_url = "/"

    def get_form(self, form_class=None):
        form = super(NewMeasurement, self).get_form(form_class)
        field = form.fields['date']
        field.initial = datetime.now()
        field.widget = AdminSplitDateTime()
        form.fields['date'] = field
        form.fields['order'].widget.attrs.update({'onchange': 'get_order_items();'})
        form.fields['examiner'].initial = self.request.user
        return form


class NewMeasurementItemAndOrder(MultiFormsView):
    template_name = 'new_item_and_order.html'
    form_classes = {'item': NewMeasurementItemForm,
                    'order': NewMeasurementOrderForm}
    success_url = '/'

    def forms_valid(self, forms, form_name=''):
        items = []
        form = forms['item']
        for sn, name in zip(form.data.getlist('sn'), form.data.getlist('name')):
            items.append(MeasurementItem.objects.get_or_create(sn=sn, name=name)[0])
        order_type = MeasurementOrderDefinition.objects.get(pk=int(forms['order'].data['order_type']))
        order = MeasurementOrder.objects.create(order_type=order_type)
        for item in items:
            order.measurement_items.add(item)
        order.save()
        return HttpResponseRedirect(self.get_success_url())

    def forms_invalid(self, forms):
        forms['sns'] = forms['item'].data.getlist('sn')
        forms['names'] = forms['item'].data.getlist('name')
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
    context['num_of_invalid'] = CharacteristicValue.objects.filter(_is_valid=False).count()
    unfinished_values = CharacteristicValue.objects.filter(_finished=False)
    context['num_not_finished'] = unfinished_values.count()
    missing_keys = {}
    for cv in unfinished_values:
        missing_keys[str(cv)] = ','.join(cv.missing_keys)
    context['missing_keys'] = missing_keys
    return render_to_response('recalc_view.html', context)


def recalculate_invalid(request):
    if request.is_ajax() and request.method == 'POST':
        invalid_values = CharacteristicValue.objects.filter(_is_valid=False)
        for val in invalid_values:
            dummy = val.value
    return JsonResponse({})


def recalculate_progress(request):
    if request.is_ajax() and request.method == 'POST' and request.POST['start_num']:
        num_invalid_val = CharacteristicValue.objects.filter(_is_valid=False).count()
        start_num = int(request.POST['start_num'])
        progress = int((start_num - num_invalid_val) * 100.0 / start_num)
        return JsonResponse(
            {'progress': str(progress), 'remaining': str(num_invalid_val), 'finished': num_invalid_val == 0})
    return JsonResponse({'progress': '0', 'remaining': '0', 'finished': True})


def plot_characteristic_values(request):
    filter_args = {}
    if request.GET:
        filter_args = request.GET.dict()
    context = {}
    values = __fetch_plot_data(filter_args)
    script = __create_plot_code(values)
    context['script'] = script
    return render_to_response('plot_charateristic_value.html', context=context)


def __create_plot_code(values, annotations=PlotAnnotationContainer()):
    annotations.add_annotation('max', FixedMaxAnnotation(2))
    annotations.add_annotation('min', FixedMinAnnotation(1))
    factors = ['{}-{}'.format(val[0], val[1]) for val in values.values]
    plot = figure(x_range=FactorRange(factors=factors))
    plot.circle(factors, values['_calc_value'], color='navy', alpha=0.5)
    plot.line(factors, values['_calc_value'], color='navy', alpha=0.5)
    plot.logo = None
    plot.xaxis.major_label_orientation = pi / 4
    plot.xaxis.major_label_standoff = 10
    min_anno, max_anno = annotations.calc_min_max_annotation(values['_calc_value'])
    range = max_anno - min_anno
    annotations.plot(plot, values['_calc_value'])
    plot.y_range.start = min_anno - range
    plot.y_range.end = max_anno + range
    session = push_session(curdoc())
    script = autoload_server(plot, session_id=session.id)
    return script


def __fetch_plot_data(filter_args, max_number=100):
    values = CharacteristicValue.objects.filter(_finished=True, **filter_args)
    return values[max(0, values.count() - max_number):].to_dataframe(
        fieldnames=['id', 'measurements__meas_item__sn', '_calc_value'])
