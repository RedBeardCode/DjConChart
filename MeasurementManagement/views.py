# Create your views here.

from django.views.generic import CreateView

from .models import Measurement


class MeasurementView(CreateView):
    template_name = "new_measurement.html"
    model = Measurement
    fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
              'meas_item', 'measurement_devices', 'raw_data_file']
