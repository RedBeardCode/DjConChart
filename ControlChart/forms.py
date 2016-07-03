#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Module for the definition of form classes
"""

from copy import copy

from django.core.exceptions import ValidationError
from django.forms import ModelForm, TextInput

from .models import MeasurementItem, MeasurementOrder


class NewMeasurementItemForm(ModelForm):
    """
    Form class for the input of new measurement items with autocomplete fields
    """

    class Meta:
        model = MeasurementItem
        fields = ["serial_nr", 'name', 'product']
        widgets = {"serial_nr": TextInput(
            attrs={'autocomplete': 'off', 'class': 'sn_autocomplete'})}

    def clean(self):
        clean_data = super(NewMeasurementItemForm, self).clean()
        if '' in self.data.getlist('serial_nr') and not self.errors:
            self.errors['serial_nr'] = ['This field is required']
        sn_list = copy(self.data.getlist('serial_nr'))
        sn_list.sort()
        while sn_list and '' in sn_list:
            sn_list.remove('')
        if len(set(sn_list)) != len(sn_list):
            raise ValidationError('Duplicated measurement item')
        return clean_data


class NewMeasurementOrderForm(ModelForm):
    """
    Form class for input of new MeasurementOrders used in combinated item and
    order form.
    """
    class Meta:
        model = MeasurementOrder
        fields = ['order_type']
