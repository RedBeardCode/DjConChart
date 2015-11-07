# Create your views here.
from datetime import datetime

from django.views.generic import CreateView
from django.contrib.admin.widgets import AdminSplitDateTime
from django.http import JsonResponse

from .models import Measurement, MeasurementOrder, CalculationRule


class NewCalculationRule(CreateView):
    template_name = "new_calculation_rule.html"
    model = CalculationRule
    fields = ['rule_name', 'rule_code']
    success_url = ''


class NewMeasurement(CreateView):
    template_name = "new_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
              'meas_item', 'measurement_devices', 'raw_data_file']

    def get_form(self, form_class=None):
        form = super(NewMeasurement, self).get_form(form_class)
        field = form.fields['date']
        field.initial = datetime.now()
        field.widget = AdminSplitDateTime()
        form.fields['date'] = field
        form.fields['order'].widget.attrs.update({'onchange': 'get_order_items();'})
        form.fields['examiner'].initial = self.request.user
        return form


def get_ajax_order_info(request):
    start_tuple = (-1, 'Please select first the order')
    items_response = {'order_items': [start_tuple], 'meas_devices': [start_tuple], 'meas_items': [start_tuple]}
    if request.is_ajax() and request.method == 'POST' and request.POST['order']:
        order_items_response = []
        meas_devices_response = []
        meas_item_response = []
        order_pk = int(request.POST['order'])
        order = MeasurementOrder.objects.get(pk=order_pk)
        order_items = order.order_type.charateristic_values.all()
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
