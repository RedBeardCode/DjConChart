from contextlib import closing
from math import pi

from bokeh.client import push_session, pull_session
from bokeh.document import Document
from bokeh.embed import autoload_server
from bokeh.models import FactorRange, ColumnDataSource, HoverTool
from bokeh.models import HBox
from bokeh.plotting import Figure
from numpy import histogram

import MeasurementManagement.models
from .plot_annotation import PlotAnnotationContainer

MAX_CALC_POINTS = 100


class PlotGenerator(object):
    def __init__(self, configuration, max_calc_points=MAX_CALC_POINTS):
        self.__conf = configuration
        self.__max_calc_points = MAX_CALC_POINTS
        self.__factors, self.__values, self.__num_invalid = self.__create_x_y_values()
        self.__document = Document()
        self.__document.title = self.__conf.description

    @property
    def num_invalid(self):
        return self.__num_invalid

    @property
    def factors(self):
        return self.__factors

    @property
    def values(self):
        return self.__values

    def __fetch_plot_data(self):

        values = MeasurementManagement.models.CharacteristicValue.objects.filter(_finished=True,
                                                                                 **self.__conf.filter_args[0])

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

    def __create_x_y_values(self):
        values, num_invalid = self.__fetch_plot_data()
        factors = self.__create_x_labels(values)
        return factors, values, num_invalid

    def create_plot_code(self):
        plot = self.__create_control_chart_hist()
        self.__document.add_root(plot)

        with closing(push_session(self.__document)) as session:
            us = MeasurementManagement.models.UserPlotSession.objects.create(bokeh_session_id=session.id,
                                                                             plot_config=self.__conf)
            script = autoload_server(None, session_id=session.id)
        return script

    def __plot_histogram(self):
        plot = Figure()
        plot.title = 'Histogram'
        hist, edges = histogram(self.__values._calc_value)
        plot.logo = None
        plot.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:],
                  fill_color="#036564", line_color="#033649")
        return plot

    def __create_control_chart_hist(self):
        plot_args = self.__conf.plot_args
        annotations = self.__conf.annotations
        if not plot_args:
            plot_args = [{}]
        if not annotations:
            annotations = PlotAnnotationContainer()
        plots = [self.__plot_control_chart(annotations, plot_args)]
        if self.__conf.histogram:
            plots.append(self.__plot_histogram())
        return HBox(*plots)

    def __plot_control_chart(self, annotations, plot_args):
        plot = Figure(x_range=FactorRange(factors=self.__factors, name='x_factors'))
        plot.logo = None
        plot.title = 'Control chart'
        hover_tool = self.__create_tooltips()
        plot.add_tools(hover_tool)
        plot.xaxis.major_label_orientation = pi / 4
        plot.xaxis.major_label_standoff = 10
        plot_args = plot_args[0]
        if not self.__values['_calc_value'].empty:
            if 'color' not in plot_args:
                plot_args['color'] = 'navy'
            if 'alpha' not in plot_args:
                plot_args['alpha'] = 0.5
            self.__values['s_fac'] = self.__factors
            col_ds = ColumnDataSource(self.__values)
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
                all_x_fac_range = session.document.select_one({'name': 'x_factors'})
                fac_ranges.remove(all_x_fac_range)
                plot_generator = PlotGenerator(us.plot_config)
                for val, s_fac, ds in zip(plot_generator.values,
                                          plot_generator.factors,
                                          data_sources):
                    val_dict = dict()
                    for key in val.keys():
                        val_dict[key] = list(val[key])
                    val_dict['s_fac'] = s_fac
                    ds.data = val_dict
                    for fac in fac_ranges:
                        fac.factors = s_fac

                all_x_fac_range.factors = plot_generator.factors
