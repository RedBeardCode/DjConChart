from django.shortcuts import render

# Create your views here.

from django.views.generic import FormView

from .forms import MeasurementForm

class MeasurementView(FormView):
    template_name = "new_measurement.html"
    form_class = MeasurementForm