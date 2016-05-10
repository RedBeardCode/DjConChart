from contextlib import closing
from math import pi

from bokeh.client import push_session, pull_session
from bokeh.document import Document
from bokeh.embed import autoload_server
from bokeh.models import FactorRange, ColumnDataSource, HoverTool
from bokeh.models import HBox
from bokeh.plotting import Figure
from django.db.models import Q
from numpy import histogram

import MeasurementManagement.models
from .plot_annotation import PlotAnnotationContainer


def create_plot_code(configuration):
    plot = __create_control_chart_hist(configuration)
    document = Document()
    document.add_root(plot)
    document.title = configuration.description

    with closing(push_session(document)) as session:
        us = MeasurementManagement.models.UserPlotSession.objects.create(bokeh_session_id=session.id,
                                                                         plot_config=configuration)
        script = autoload_server(None, session_id=session.id)
    return script


def __plot_histogram(all_values):
    plot = Figure()
    plot.title = 'Histogram'
    hist, edges = histogram(all_values._calc_value)
    plot.logo = None
    plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
              fill_color="#036564", line_color="#033649")
    return plot


def __create_control_chart_hist(configuration):
    num_filter_args = len(configuration.filter_args)
    plot_args = configuration.plot_args
    annotations = configuration.annotations
    if not plot_args:
        plot_args = [{}]
    if len(plot_args) < num_filter_args:
        plot_args = plot_args + [{}] * (num_filter_args - len(plot_args))
    if not annotations:
        annotations = PlotAnnotationContainer()
    factors, single_factors, values, all_values = __create_x_y_values(configuration.filter_args)
    plots = list()
    plots.append(__plot_control_chart(annotations, factors, plot_args, single_factors, values, all_values))
    if configuration.histogram:
        plots.append(__plot_histogram(all_values))
    return HBox(*plots)


def __plot_control_chart(annotations, factors, plot_args, single_factors, values, all_values):
    plot = Figure(x_range=FactorRange(factors=factors, name='all_x_factors'))

    plot.logo = None
    plot.title = 'Control chart'
    hover_tool = __create_tooltips()
    plot.add_tools(hover_tool)
    plot.xaxis.major_label_orientation = pi / 4
    plot.xaxis.major_label_standoff = 10
    for s_fac, val, pl_arg in zip(single_factors, values, plot_args):
        if not val['_calc_value'].empty:
            if 'color' not in pl_arg:
                pl_arg['color'] = 'navy'
            if 'alpha' not in pl_arg:
                pl_arg['alpha'] = 0.5
            val['s_fac'] = s_fac
            col_ds = ColumnDataSource(val)
            plot.circle('s_fac', '_calc_value', source=col_ds, name='circle', **pl_arg)
            plot.line('s_fac', '_calc_value', source=col_ds, name='line', **pl_arg)
    min_anno, max_anno = annotations.calc_min_max_annotation(val['_calc_value'])
    annotations.plot(plot, val['_calc_value'])
    range = max_anno - min_anno
    if range:
        plot.y_range.start = min_anno - range
        plot.y_range.end = max_anno + range
    return plot


def __create_tooltips():
    tooltips = """
    <div>
    <small>
    <em><strong> @order__order_type__name: @order__order_nr</strong></em>
     <ul>
     <li>Serial: @measurements__meas_item__sn</li>
     <li>Value: @_calc_value</li>
     <li>Date: @date</li>
     <li>Examiner: @measurements__examiner</li>
     <li>Remarks: @measurements__remarks</li>
     </ul>
     </small>
    </div>
    """
    hover_tool = HoverTool(tooltips=tooltips)
    return hover_tool


def __create_x_y_values(filter_args):
    single_factors = []
    values = []
    combined_filters = Q()
    for index, fi_arg in enumerate(filter_args):
        values.append(__fetch_plot_data(fi_arg))
        s_fac = __create_x_labels(values[index])
        single_factors.append(s_fac)
        combined_filters |= Q(**fi_arg)
    all_values = __fetch_plot_data(combined_filters)
    factors = __create_x_labels(all_values)
    return factors, single_factors, values, all_values


def __create_x_labels(values):
    return ['{}-{}'.format(id, sn) for id, sn in zip(values['id'], values['measurements__meas_item__sn'])]


def __fetch_plot_data(filter_args, max_number=100):
    if isinstance(filter_args, Q):
        values = MeasurementManagement.models.CharacteristicValue.objects.filter(filter_args, _finished=True)
    else:
        values = MeasurementManagement.models.CharacteristicValue.objects.filter(_finished=True, **filter_args)

    dt = values[max(0, values.count() - max_number):].to_dataframe(
        fieldnames=['id', 'measurements__meas_item__sn', '_calc_value', 'date', 'order__order_type__name',
                    'order__order_nr', 'measurements__examiner', 'measurements__remarks'])
    dt['date'] = dt['date'].dt.strftime('%Y-%m-%d %H:%M')
    grouped = dt.groupby('id')

    def combine_it(val_set):
        return '; '.join(val_set)

    def take_first(val_set):
        return val_set[:1]

    dt = grouped.agg({'id': take_first,
                      'measurements__meas_item__sn': take_first,
                      '_calc_value': take_first,
                      'date': take_first,
                      'order__order_type__name': take_first,
                      'order__order_nr': take_first,
                      'measurements__examiner': combine_it,
                      'measurements__remarks': combine_it})
    return dt


def update_plot_sessions():
    for us in MeasurementManagement.models.UserPlotSession.objects.all():
        with closing(pull_session(session_id=us.bokeh_session_id)) as session:
            if len(session.document.roots) == 0:
                # In this case, the session_id was from a dead session and
                # calling pull_session caused a new empty session to be
                # created. So we just delete the UserSession and move on.
                # It would be nice if there was a more efficient way - where I
                # could just ask bokeh if session x is a session.
                us.delete()
            else:
                data_sources = list(session.document.select({'type': ColumnDataSource}))
                fac_ranges = list(session.document.select({'type': FactorRange}))
                all_x_fac_range = session.document.select_one({'name': 'all_x_factors'})
                fac_ranges.remove(all_x_fac_range)
                factors, single_factors, values, dummy = __create_x_y_values(us.plot_config.filter_args)

                for val, s_fac, ds in zip(values, single_factors, data_sources):
                    val_dict = dict()
                    for key in val.keys():
                        val_dict[key] = list(val[key])
                    val_dict['s_fac'] = s_fac
                    ds.data = val_dict
                    for fac in fac_ranges:
                        fac.factors = s_fac

                all_x_fac_range.factors = factors
