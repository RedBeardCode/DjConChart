# Create your views here.
from django.views.generic import CreateView
from django.contrib.admin.widgets import AdminSplitDateTime
from django.http import JsonResponse

from .models import Measurement, CharacteristicValueDescription, MeasurementOrder


class MeasurementView(CreateView):
    template_name = "new_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
              'meas_item', 'measurement_devices', 'raw_data_file']

    def get_form(self, form_class=None):
        form = super(MeasurementView, self).get_form(form_class)
        field = form.fields['date']
        field.widget = AdminSplitDateTime()
        form.fields['date'] = field
        form.fields['order'].widget.attrs.update({'onchange': 'get_order_items();'})
        form.fields['order_items'].queryset = CharacteristicValueDescription.objects.none()
        return form


def get_ajax_order_info(request):
    items_response = [{'pk': -1, 'label': 'Please select first the order'}]
    if request.is_ajax() and request.method == 'POST' and request.POST['order']:
        items_response = []
        order_pk = int(request.POST['order'])
        order = MeasurementOrder.objects.get(pk=order_pk)
        items = order.order_type.charateristic_values.all()
        for item in items:
            items_response.append({'pk': item.pk, 'label': item.description})
    return JsonResponse({'order_items': items_response})
