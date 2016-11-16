#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Offers different annotation for the plot like mean, lower control limit, upper
control limit etc. Use one of this classes as base to create your own
annotations.
"""

from bokeh.models import BoxAnnotation


class PlotAnnotation(object):
    """
    Base class for all annotation. With annotation it is possible to show
    colored y-ranges or horizontal lines to mark special areas in the plot.
    """
    UPPER_CONTROL_LIMIT_LEVEL = 3
    LOWER_CONTROL_LIMIT_LEVEL = 2

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def bottom(self, y_values):  # pylint: disable=W0613, R0201
        """
        Returns bottom value of the annotation calculated out of the y_values.
        This method must be overridden by each implementation of a
        PlotAnnotation
        """
        raise NotImplementedError('Bottom calculation for a PlotAnnotation'
                                  'isn`t defined')

    def top(self, y_values):  # pylint: disable=W0613, R0201
        """
        Returns top value of the annotation calculated out of the y_values.
        This method must be overridden by each implementation of a
        PlotAnnotation.
        """
        raise NotImplementedError('Bottom calculation for a PlotAnnotation'
                                  'isn`t defined')


class MeanAnnotation(PlotAnnotation):
    """
    Annotation to mark the mean of a plot
    """
    def __init__(self, line_color='green', line_alpha=1.0, **kwargs):
        super(MeanAnnotation, self).__init__(line_color=line_color,
                                             line_alpha=line_alpha,
                                             **kwargs)

    def bottom(self, y_values):
        """
        Returns the mean value
        """
        return y_values.mean()

    def top(self, y_values):
        """
        Returns the mean value
        """
        return y_values.mean()


class MultiStdAnnotation(PlotAnnotation):
    """
    Annotation to mark a area with the width factor*std around the mean of the
    plot
    """

    def __init__(self, factor, fill_color='red', fill_alpha=0.0,
                 # pylint: disable=R0913
                 line_color='red', line_alpha=0.6, line_dash='dashed',
                 **kwargs):
        super(MultiStdAnnotation, self).__init__(fill_color=fill_color,
                                                 fill_alpha=fill_alpha,
                                                 line_color=line_color,
                                                 line_alpha=line_alpha,
                                                 line_dash=line_dash,
                                                 **kwargs)
        self.__factor = factor

    def bottom(self, y_values):
        """
        Returns mean - factor*std
        """
        return y_values.mean() - (y_values.std() * self.__factor)

    def top(self, y_values):
        """
        Returns mean + factor*std
        """
        return y_values.mean() + (y_values.std() * self.__factor)


class UpperControlLimitAnnotation(MultiStdAnnotation):
    """
    Show the upper control limit (UCL)
    """
    def __init__(self, line_alpha=1.0, **kwargs):
        super(UpperControlLimitAnnotation, self).__init__(
            PlotAnnotation.UPPER_CONTROL_LIMIT_LEVEL,
            line_alpha=line_alpha,
            **kwargs)


class LowerControlLimitAnnotation(MultiStdAnnotation):
    """
    Show the lower control limit (LCL)
    """
    def __init__(self, **kwargs):
        super(LowerControlLimitAnnotation, self).__init__(
            PlotAnnotation.LOWER_CONTROL_LIMIT_LEVEL, **kwargs)


class FixedMaxAnnotation(PlotAnnotation):
    """
    Marks all over the given maximum bottom level
    """
    def __init__(self, max_bottom, fill_color='red', **kwargs):
        super(FixedMaxAnnotation, self).__init__(fill_color=fill_color,
                                                 **kwargs)
        self.__max_bottom = max_bottom

    def bottom(self, y_values):
        return self.__max_bottom

    def top(self, y_values):
        return None


class FixedMinAnnotation(PlotAnnotation):
    """
    Marks all under the given minimum bottom level
    """
    def __init__(self, min_top, fill_color='red', **kwargs):
        super(FixedMinAnnotation, self).__init__(fill_color=fill_color,
                                                 **kwargs)
        self.__min_top = min_top

    def bottom(self, y_values):
        return None

    def top(self, y_values):
        return self.__min_top


class PlotAnnotationContainer(object):
    """
    Bundles all annotations of a plot
    """
    def __init__(self, create_default=True):
        self.__annotations = {}
        if create_default:
            self.create_default_annotations()

    def create_default_annotations(self):
        """
        Creates a mean, upper control limit and lower control limit as a default
        set of annotations.
        """
        self.__annotations['mean'] = MeanAnnotation()
        self.__annotations['ucl'] = UpperControlLimitAnnotation()
        self.__annotations['lcl'] = LowerControlLimitAnnotation()

    def plot(self, plot, y_values):
        """
        Adds the annotations to the plot
        :param plot: Bokeh plot to add the annotations
        :param y_values: y-values of the plot
        """
        if y_values.empty:
            return
        for name in self.__annotations:
            plot.add_layout(BoxAnnotation(
                bottom=self.__annotations[name].bottom(y_values),
                top=self.__annotations[name].top(y_values),
                **self.__annotations[name].kwargs))

    def calc_min_max_annotation(self, y_values):
        """
        Calculates the borders of all annotations and returns the exterma
        :param y_values: y-values of the plot
        :return: min and max value reached by one annotation
        """
        bottoms = []
        tops = []
        for name in self.__annotations:
            if self.__annotations[name].bottom(y_values):
                bottoms.append(self.__annotations[name].bottom(y_values))
            if self.__annotations[name].top(y_values):
                tops.append(self.__annotations[name].top(y_values))
        return min(bottoms), max(tops)

    def add_annotation(self, key, annotation):
        """
        Add an annotation to the container
        """
        self.__annotations[key] = annotation

    def remove_annotation(self, key):
        """
        Removes the annotation with the given key
        """
        self.__annotations.pop(key)

    def count(self):
        """
        Returns the number of annotations
        """
        return len(self.__annotations)

    def keys(self):
        """
        List of keys
        """
        return self.__annotations.keys()
