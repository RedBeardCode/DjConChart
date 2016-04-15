# Create your views here.
from datetime import datetime
from math import pi

from bokeh.client import push_session
from bokeh.embed import autoload_server
from bokeh.models import FactorRange, HoverTool, ColumnDataSource
from bokeh.plotting import figure, curdoc
from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.urlresolvers import reverse_lazy
from django.db.models import Q
from django.http import JsonResponse, HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.views.generic import CreateView, ListView, UpdateView, DeleteView

from MeasurementManagement.plot_annotation import PlotAnnotationContainer
from .forms import NewMeasurementItemForm, NewMeasurementOrderForm
from .models import CharacteristicValueDescription, PlotConfig
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

        return context


class NewCharacteristicValueDescription(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = CharacteristicValueDescription
    fields = ['value_name', 'description', 'calculation_rule', 'possible_meas_devices']
    success_url = '/'


class DeleteCharacteristicValueDescription(DeleteView):
    template_name = "delete_base.html"
    model = CharacteristicValueDescription
    success_url = reverse_lazy('list_characteristic_value_description')


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


class ListCharacteristicValueDescription(TitledListView):
    template_name = "list_characteristic_value_description.html"
    model = CharacteristicValueDescription
    fields = ['value_name', 'description', 'calculation_rule', 'possible_meas_devices']


# TODO: Links für Zürck und Delete Buttons, Weiter Models

class UpdateCharacteristicValueDescription(AddContextInfoMixIn, UpdateView):
    template_name = "new_base.html"
    model = CharacteristicValueDescription
    fields = ['value_name', 'description', 'calculation_rule', 'possible_meas_devices']
    success_url = '/'


class NewMeasurementDevice(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementDevice
    fields = ['name', 'sn']
    success_url = '/'


class NewMeasurementOrder(AddContextInfoMixIn, CreateView):
    template_name = "new_measurement_order.html"
    model = MeasurementOrder
    fields = ['order_type', 'measurement_items']
    success_url = '/'


class NewMeasurementOrderDefinition(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementOrderDefinition
    fields = ['name', 'characteristic_values', 'product']
    success_url = '/'


class NewMeasurementItem(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementItem
    fields = ['sn', 'name', 'product']
    success_url = '/'


class NewCalculationRule(AddContextInfoMixIn, CreateView):
    template_name = "new_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name', 'rule_code']
    success_url = '/'


class NewMeasurementTag(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = MeasurementTag
    fields = ['name']
    success_url = "/"


class NewProduct(AddContextInfoMixIn, CreateView):
    template_name = "new_base.html"
    model = Product
    fields = ['product_name']
    success_url = "/"


class NewMeasurement(AddContextInfoMixIn, CreateView):
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
    context['num_of_invalid'] = CharacteristicValue.objects.filter(_is_valid=False, _finished=True).count()
    unfinished_values = CharacteristicValue.objects.filter(_finished=False)
    context['num_not_finished'] = unfinished_values.count()
    missing_keys = {}
    for cv in unfinished_values:
        missing_keys[str(cv)] = ','.join(cv.missing_keys)
    context['missing_keys'] = missing_keys
    return render_to_response('recalc_view.html', context)


def recalculate_invalid(request):
    if request.is_ajax() and request.method == 'POST':
        invalid_values = CharacteristicValue.objects.filter(_is_valid=False, _finished=True)
        for val in invalid_values:
            dummy = val.value
    return JsonResponse({})


def recalculate_progress(request):
    if request.is_ajax() and request.method == 'POST' and request.POST['start_num']:
        num_invalid_val = CharacteristicValue.objects.filter(_is_valid=False, _finished=True).count()
        start_num = int(request.POST['start_num'])
        progress = int((start_num - num_invalid_val) * 100.0 / start_num)
        return JsonResponse(
            {'progress': str(progress), 'remaining': str(num_invalid_val), 'finished': num_invalid_val == 0})
    return JsonResponse({'progress': '0', 'remaining': '0', 'finished': True})


def plot_characteristic_values(request):
    # Todo: Is replaced through plot_given_configuration
    filter_args = {}
    if request.GET:
        filter_args = request.GET.dict()
    context = {}
    script = __create_plot_code([filter_args])
    context['script'] = script
    return render_to_response('single_plot.html', context=context)


def __create_plot_code(filter_args, plot_args=[{}], annotations=None):
    num_filter_args = len(filter_args)
    if not plot_args:
        plot_args = [{}]
    if len(plot_args) < num_filter_args:
        plot_args = plot_args + [{}] * (num_filter_args - len(plot_args))
    if not annotations:
        annotations = PlotAnnotationContainer()
    plot = None
    factors, single_factors, values, all_values = __create_x_y_values(filter_args)
    plot = __plot_values(annotations, factors, plot, plot_args, single_factors, values, all_values)
    session = push_session(curdoc())
    script = autoload_server(plot, session_id=session.id)
    return script


def __plot_values(annotations, factors, plot, plot_args, single_factors, values, all_values):
    plot = figure(x_range=FactorRange(factors=factors))
    plot.logo = None
    hover_tool = __create_tooltips()
    plot.add_tools(hover_tool)
    plot.xaxis.major_label_orientation = pi / 4
    plot.xaxis.major_label_standoff = 10
    for s_fac, val, pl_arg in zip(single_factors, values, plot_args):
        if not val['_calc_value'].empty:
            if 'color' not in pl_arg:
                pl_arg['color'] = 'navy'
            if 'alpha' not in pl_arg:
                pl_arg['alpha'] = 0.5
            plot.circle(s_fac, '_calc_value', source=ColumnDataSource(val), **pl_arg)
            plot.line(s_fac, '_calc_value', source=ColumnDataSource(val), **pl_arg)
    min_anno, max_anno = annotations.calc_min_max_annotation(val['_calc_value'])
    annotations.plot(plot, val['_calc_value'])
    range = max_anno - min_anno
    if range:
        plot.y_range.start = min_anno - range
        plot.y_range.end = max_anno + range
    return plot


def __create_tooltips():
    tooltips = """
    <div>
    <small>
    <em><strong> @order__order_type__name: @order__order_nr</strong></em>
     <ul>
     <li>Serial: @measurements__meas_item__sn</li>
     <li>Value: @_calc_value</li>
     <li>Date: @date</li>
     <li>Examiner: @measurements__examiner</li>
     <li>Remarks: @measurements__remarks</li>
     </ul>
     </small>
    </div>
    """
    hover_tool = HoverTool(tooltips=tooltips)
    return hover_tool


def __create_x_y_values(filter_args):
    single_factors = []
    values = []
    combined_filters = Q()
    for index, fi_arg in enumerate(filter_args):
        values.append(__fetch_plot_data(fi_arg))
        s_fac = __create_x_labels(values[index])
        single_factors.append(s_fac)
        combined_filters |= Q(**fi_arg)
    all_values = __fetch_plot_data(combined_filters)
    factors = __create_x_labels(all_values)
    return factors, single_factors, values, all_values


def __create_x_labels(values):
    return ['{}-{}'.format(id, sn) for id, sn in zip(values['id'], values['measurements__meas_item__sn'])]



def __fetch_plot_data(filter_args, max_number=100):
    if isinstance(filter_args, Q):
        values = CharacteristicValue.objects.filter(filter_args, _finished=True)
    else:
        values = CharacteristicValue.objects.filter(_finished=True, **filter_args)

    dt = values[max(0, values.count() - max_number):].to_dataframe(
        fieldnames=['id', 'measurements__meas_item__sn', '_calc_value', 'date', 'order__order_type__name',
                    'order__order_nr', 'measurements__examiner', 'measurements__remarks'])
    dt['date'] = dt['date'].dt.strftime('%Y-%m-%d %H:%M')
    grouped = dt.groupby('id')

    def combine_it(val_set):
        return '; '.join(val_set)

    def take_first(val_set):
        return val_set[:1]

    dt = grouped.agg({'id': take_first,
                      'measurements__meas_item__sn': take_first,
                      '_calc_value': take_first,
                      'date': take_first,
                      'order__order_type__name': take_first,
                      'order__order_nr': take_first,
                      'measurements__examiner': combine_it,
                      'measurements__remarks': combine_it})
    return dt

def plot_given_configuration(request, configuration):
    try:
        plot_config = PlotConfig.objects.get(short_name=configuration)
    except PlotConfig.DoesNotExist:
        raise Http404
    script = __create_plot_code(plot_config.filter_args,
                                plot_config.plot_args,
                                annotations=plot_config.get_annotation_container())
    context = {'script': script}
    return render_to_response('single_plot.html', context=context)
