import os
from contextlib import closing
from math import pi

from bokeh.client import pull_session as bokeh_pull_session
from bokeh.client import push_session as bokeh_push_session
from bokeh.document import Document
from bokeh.embed import autoload_server as bokeh_autoload_server
from bokeh.models import FactorRange, ColumnDataSource, HoverTool
from bokeh.models import HBox
from bokeh.plotting import Figure
from numpy import histogram

import MeasurementManagement.models
from .plot_annotation import PlotAnnotationContainer, PlotAnnotation

MAX_CALC_POINTS = 100

def push_session(*args, **kwargs):
    if 'BOKEH_SERVER' in os.environ:
        kwargs['url'] = os.environ['BOKEH_SERVER']
    return bokeh_push_session(*args, **kwargs)

def pull_session(*args, **kwargs):
    if 'BOKEH_SERVER' in os.environ:
        kwargs['url'] = os.environ['BOKEH_SERVER']
    return bokeh_pull_session(*args, **kwargs)

def autoload_server(*args, **kwargs):
    if 'BOKEH_SERVER' in os.environ:
        kwargs['url'] = os.environ['BOKEH_SERVER']
    return bokeh_autoload_server(*args, **kwargs)

class PlotGenerator(object):
    def __init__(self, configuration, index=None, max_calc_points=MAX_CALC_POINTS):
        self.__conf = configuration
        self.__index = None
        if index != None:
            self.__index = int(index)
        self.__max_calc_points = MAX_CALC_POINTS
        self.__factors, self.__values, self.__num_invalid = [], [], []

    def __fetch_plot_data(self, filter_args):

        values = MeasurementManagement.models.CharacteristicValue.objects.filter(_finished=True,
                                                                                 **filter_args)

        dt = values[max(0, values.count() - self.__max_calc_points):].to_dataframe(
            fieldnames=['id', 'measurements__meas_item__sn', '_calc_value', 'date', 'order__order_type__name',
                        'order__order_nr', 'measurements__examiner', 'measurements__remarks'])
        if not dt.date.empty:
            dt['date'] = dt.date.dt.strftime('%Y-%m-%d %H:%M')
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
        return dt, values.count_invalid()

    def __create_x_labels(self, values):
        return ['{}-{}'.format(id, sn) for id, sn in zip(values['id'], values['measurements__meas_item__sn'])]

    def create_x_y_values(self, index):
        filter_args = self.__conf.filter_args[index]
        values, num_invalid = self.__fetch_plot_data(filter_args)
        factors = self.__create_x_labels(values)
        return factors, values, num_invalid

    def __save_user_session(self, document, index):
        with closing(push_session(document)) as session:
            session_id = session.id
            us = MeasurementManagement.models.UserPlotSession.objects.create(bokeh_session_id=session.id,
                                                                             plot_config=self.__conf,
                                                                             index=index)
        return session_id

    def create_plot_code_iterator(self):

        for index, dummy in enumerate(self.__conf.filter_args):
            if self.__index != None and self.__index != index:
                continue
            document = Document()
            document.title = self.__conf.description
            self.__factors, self.__values, num_invalid = self.create_x_y_values(index)
            plot = self.__create_control_chart_hist(index)
            document.add_root(plot)
            session_id = self.__save_user_session(document, index)
            script = autoload_server(None, session_id=session_id)
            yield script, num_invalid

    def __plot_histogram(self):
        plot = Figure(plot_height=600, plot_width=400)
        plot.title = 'Histogram'
        hist_data = self.calc_histogram_data(self.__values)
        plot.logo = None
        plot.quad(top='hist', bottom=0, left='edges_left', right='edges_right', source=hist_data,
                  fill_color="#036564", line_color="#033649")
        return plot

    def calc_histogram_data(self, values):
        hist, edges = histogram(values._calc_value)
        hist_data = dict()
        hist_data['hist'] = hist
        hist_data['edges_left'] = edges[:-1]
        hist_data['edges_right'] = edges[1:]
        return ColumnDataSource(hist_data, name='hist_data')

    def __create_control_chart_hist(self, index):

        plots = [self.__plot_control_chart(index)]
        if self.__conf.histogram:
            plots.append(self.__plot_histogram())
        return HBox(*plots)

    def __plot_control_chart(self, index):
        plot_args = self.__conf.plot_args[index]
        annotations = self.__conf.annotations[index]
        if not annotations:
            annotations = PlotAnnotationContainer()
        plot = Figure(plot_height=600, plot_width=800,
                      x_range=FactorRange(factors=self.__factors, name='x_factors'))
        plot.logo = None
        plot.title = 'Control chart'
        hover_tool = self.__create_tooltips()
        plot.add_tools(hover_tool)
        plot.xaxis.major_label_orientation = pi / 4
        plot.xaxis.major_label_standoff = 10
        if not self.__values['_calc_value'].empty:
            if 'color' not in plot_args:
                plot_args['color'] = 'navy'
            if 'alpha' not in plot_args:
                plot_args['alpha'] = 0.5
            self.__values['s_fac'] = self.__factors
            col_ds = ColumnDataSource(self.__values, name='control_data')
            plot.circle('s_fac', '_calc_value', source=col_ds, name='circle', **plot_args)
            plot.line('s_fac', '_calc_value', source=col_ds, name='line', **plot_args)
        min_anno, max_anno = annotations.calc_min_max_annotation(self.__values['_calc_value'])
        annotations.plot(plot, self.__values['_calc_value'])
        range = max_anno - min_anno
        if range:
            plot.y_range.start = min_anno - range
            plot.y_range.end = max_anno + range
        return plot

    def __create_tooltips(self):
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

    def values_for_last_plot(self):
        return self.__values

    def summary_for_last_plot(self):
        return self.__values._calc_value.mean(), \
               PlotAnnotation.LOWER_INTERVENTION_LEVEL * self.__values._calc_value.std(), \
               PlotAnnotation.UPPER_INTERVENTION_LEVEL * self.__values._calc_value.std()



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
                control_sources = list(session.document.select({'name': 'control_data'}))
                hist_sources = list(session.document.select({'name': 'hist_data'}))
                fac_ranges = list(session.document.select({'type': FactorRange}))
                all_x_fac_range = session.document.select_one({'name': 'x_factors'})
                fac_ranges.remove(all_x_fac_range)
                plot_generator = PlotGenerator(us.plot_config)
                factors, values, _ = plot_generator.create_x_y_values(us.index)
                val_dict = dict()
                for key in values.keys():
                    val_dict[key] = list(values[key])
                val_dict['s_fac'] = factors
                for cs in control_sources:
                    cs.data = val_dict
                hist_data = plot_generator.calc_histogram_data(values)
                for hs in hist_sources:
                    hs.data = hist_data.data
                for fac in fac_ranges:
                    fac.factors = factors

                all_x_fac_range.factors = factors
