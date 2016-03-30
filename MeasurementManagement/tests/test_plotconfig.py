import pytest
from bokeh.client import pull_session

from MeasurementManagement.models import PlotConfig
from MeasurementManagement.plot_annotation import MeanAnnotation, UpperInterventionAnnotation, \
    LowerInterventionAnnotation
from MeasurementManagement.tests.utilies import login_as_admin, create_correct_sample_data, \
    create_sample_characteristic_values


@pytest.mark.django_db
def test_filter_args():
    plot_config = PlotConfig.objects.create(description='filter args test', short_name='filter_args')
    filter_args = [{'product__id': 1, 'finished': True}]
    assert not plot_config._PlotConfig__last_filter_args
    plot_config.filter_args = filter_args
    assert plot_config._PlotConfig__last_filter_args == filter_args
    assert plot_config.filter_args == filter_args
    plot_config.save()
    plot_config.refresh_from_db()
    assert not plot_config._PlotConfig__last_filter_args
    assert plot_config.filter_args == filter_args
    assert plot_config._PlotConfig__last_filter_args == filter_args


@pytest.mark.django_db
def test_plot_args():
    plot_config = PlotConfig.objects.create(description='plot_args_test', short_name='plot_args')
    plot_args = [{'linecolor': 'blue', 'title': 'testival'}]
    assert not plot_config._PlotConfig__last_plot_args
    plot_config.plot_args = plot_args
    assert plot_config._PlotConfig__last_plot_args == plot_args
    assert plot_config.plot_args == plot_args
    plot_config.save()
    plot_config.refresh_from_db()
    assert not plot_config._PlotConfig__last_plot_args
    assert plot_config.plot_args == plot_args
    assert plot_config._PlotConfig__last_plot_args == plot_args


@pytest.mark.django_db
def test_plot_annotations():
    plot_config = PlotConfig.objects.create(description='annotation_test', short_name='annotation')
    annotations = {'mean': MeanAnnotation(),
                   'upper': UpperInterventionAnnotation(),
                   'lower': LowerInterventionAnnotation()}
    assert not plot_config._PlotConfig__last_annotations
    plot_config.annotations = annotations
    assert plot_config._PlotConfig__last_annotations == annotations
    plot_config.save()
    plot_config.refresh_from_db()
    assert not plot_config._PlotConfig__last_annotations
    assert plot_config.annotations.keys() == annotations.keys()
    assert plot_config._PlotConfig__last_annotations
    for key in plot_config.annotations:
        assert key in annotations
        assert type(plot_config.annotations[key]) == type(annotations[key])


@pytest.mark.django_db
def test_plot_url(admin_client, live_server, webdriver):
    create_correct_sample_data()
    create_sample_characteristic_values()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/url/')
        login_as_admin(selenium)
        assert selenium.title == 'Page Not Found :('
        plot_config = PlotConfig.objects.create(description='url_test', short_name='url')
        plot_config.filter_args = [{'value__gt': 0.0}]
        plot_config.save()
        try:
            selenium.get(live_server + '/plot/url/')
            pull_session()
            assert selenium.find_element_by_class_name('bokeh-container')
        except IOError:
            # no bokeh server running
            assert selenium.find_element_by_tag_name('body').text == 'Server Error (500)'
    finally:
        selenium.close()

# TODO: Next Issuses Multiple Plots and Product view
