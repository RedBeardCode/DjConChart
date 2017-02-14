#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Extending the control_chart views with map views
"""

import json
from django.core.serializers import serialize
from django.http import JsonResponse
from django.shortcuts import render_to_response

from control_chart.views import create_plot_context
from control_chart.models import CharacteristicValue


def plot_given_configuration(request, configuration, index=None):
    """
    Replacing the plot_page templage with an template with map views
    """
    context, _ = create_plot_context(request, configuration, index)
    return render_to_response('geo_plot_page.html', context=context)


def create_map_data(request):
    """
    Ajax view to return the geo data to the leaflet init function
    """
    if request.is_ajax() and request.method == 'POST':
        filter_index = int(request.POST['filter_index'])
        filter_args = json.loads(
            request.POST.getlist('filter_args[]')[filter_index])
        values = CharacteristicValue.objects.filter(
            _finished=True,
            **filter_args)
        context = {}
        context['data'] = serialize('geojson', values,
                                    geometry_field='position')
        data_val = [val.value for val in values]
        context['heat_data'] = [(val.position.coords[1],
                                 val.position.coords[0],
                                 val.value) for val in values]
        context['heat_max'] = max(data_val)

        return JsonResponse(context)
    return JsonResponse({})
