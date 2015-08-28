__author__ = 'farmer'

from django.forms import ModelForm

from .models import Measurement

class MeasurementForm(ModelForm):
    class Meta:
        model = Measurement
        fields = ['date', 'order', 'order_items', 'examiner', 'remarks',
                  'meas_item', 'measurement_devices', 'raw_data_file']
