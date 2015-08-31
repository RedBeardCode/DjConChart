# Create your views here.

from django.views.generic import CreateView
from django.contrib.admin.widgets import AdminSplitDateTime

from .models import Measurement


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
        return form
