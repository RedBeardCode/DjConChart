from copy import copy

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput

from .models import MeasurementItem, MeasurementOrder


class NewMeasurementItemForm(ModelForm):
    class Meta:
        model = MeasurementItem
        fields = ['sn', 'name']
        widgets = {'sn': TextInput(attrs={'autocomplete': 'off', 'class': 'sn_autocomplete'})}

    def clean(self):
        clean_data = super(NewMeasurementItemForm, self).clean()
        if '' in self.data.getlist('sn') and not self.errors:
            self.errors['sn'] = ['This field is required']
        sn_list = copy(self.data.getlist('sn'))
        sn_list.sort()
        while sn_list and '' in sn_list:
            sn_list.remove('')
        if len(set(sn_list)) != len(sn_list):
            raise ValidationError('Duplicated measurement item')
        return clean_data

class NewMeasurementOrderForm(ModelForm):
    class Meta:
        model = MeasurementOrder
        fields = ['order_type']
