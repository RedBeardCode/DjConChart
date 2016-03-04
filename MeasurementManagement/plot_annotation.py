from bokeh.models import BoxAnnotation


class PlotAnnotation(object):
    UPPER_INTERVENTION_LEVEL = 3
    LOWER_INTERVENTION_LEVEL = 2

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def bottom(self, y_values):
        raise NotImplemented('Bottom calculation for a PlotAnnotation isn`t defined')

    def top(self, y_values):
        raise NotImplemented('Bottom calculation for a PlotAnnotation isn`t defined')


class MeanAnnotation(PlotAnnotation):
    def __init__(self, line_color='green', line_alpha=1.0, **kwargs):
        super(MeanAnnotation, self).__init__(line_color=line_color, line_alpha=line_alpha, **kwargs)

    def bottom(self, y_values):
        return y_values.mean()

    def top(self, y_values):
        return y_values.mean()


class MultiStdAnnotation(PlotAnnotation):
    def __init__(self, factor, fill_color='None', fill_alpha=0.0,
                 line_color='red', line_alpha=0.6, line_dash='dashed', **kwargs):
        super(MultiStdAnnotation, self).__init__(fill_color=fill_color, fill_alpha=fill_alpha,
                                                 line_color=line_color, line_alpha=line_alpha, line_dash=line_dash,
                                                 **kwargs)
        self.__factor = factor

    def bottom(self, y_values):
        return y_values.mean() - (y_values.std() * self.__factor)

    def top(self, y_values):
        return y_values.mean() + (y_values.std() * self.__factor)


class UpperInterventionAnnotation(MultiStdAnnotation):
    def __init__(self, line_alpha=1.0, **kwargs):
        super(UpperInterventionAnnotation, self).__init__(PlotAnnotation.UPPER_INTERVENTION_LEVEL,
                                                          line_alpha=line_alpha, **kwargs)


class LowerInterventionAnnotation(MultiStdAnnotation):
    def __init__(self, **kwargs):
        super(LowerInterventionAnnotation, self).__init__(PlotAnnotation.LOWER_INTERVENTION_LEVEL, **kwargs)


class PlotAnnotationContainer(object):
    def __init__(self, create_default=True):
        self.__annotations = {}
        if create_default:
            self.create_default_annotations()

    def create_default_annotations(self):
        self.__annotations['mean'] = MeanAnnotation()
        self.__annotations['upper_intervention'] = UpperInterventionAnnotation()
        self.__annotations['lower_intervention'] = LowerInterventionAnnotation()

    def plot(self, plot, y_values):
        for name in self.__annotations:
            plot.add_layout(BoxAnnotation(bottom=self.__annotations[name].bottom(y_values),
                                          top=self.__annotations[name].top(y_values),
                                          **self.__annotations[name].kwargs))

    def calc_min_max_annotation(self, y_values):
        bottoms = []
        tops = []
        for name in self.__annotations:
            if self.__annotations[name].bottom(y_values):
                bottoms.append(self.__annotations[name].bottom(y_values))
            if self.__annotations[name].top(y_values):
                tops.append(self.__annotations[name].top(y_values))
        return min(bottoms), max(tops)

    def add_annotation(self, name, annotation):
        self.__annotations[name] = annotation

    def remove_annotation(self, name):
        self.__annotations.pop(name)
