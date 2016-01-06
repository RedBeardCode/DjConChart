from django.forms import ModelForm

from .models import MeasurementItem, MeasurementOrder


class NewMeasurementItemForm(ModelForm):
    class Meta:
        model = MeasurementItem
        fields = ['sn', 'name']


class NewMeasurementOrderForm(ModelForm):
    class Meta:
        model = MeasurementOrder
        fields = ['order_type']
