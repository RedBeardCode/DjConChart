# Create your views here.
from datetime import datetime

from django.views.generic import CreateView
from django.contrib.admin.widgets import AdminSplitDateTime
from django.http import JsonResponse, HttpResponseRedirect

from .models import Measurement, MeasurementOrder, CalculationRule
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


class NewMeasurement(CreateView):
    template_name = "new_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
              'meas_item', 'measurement_devices', 'raw_data_file']
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
