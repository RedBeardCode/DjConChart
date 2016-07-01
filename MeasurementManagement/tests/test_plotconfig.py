#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest

from MeasurementManagement.models import PlotConfig
from .utilies import create_correct_sample_data, create_limited_users
from .utilies import create_sample_characteristic_values, create_plot_config
from .utilies import login_as_admin
from ..plot_annotation import LowerControlLimitAnnotation
from ..plot_annotation import MeanAnnotation, UpperControlLimitAnnotation
from ..plot_util import PlotGenerator, pull_session


@pytest.mark.django_db
def test_filter_args():
    plot_config = PlotConfig.objects.create(description='filter args test',
                                            short_name='filter_args')
    filter_args = [{'product__id': 1, 'finished': True}]
    assert not plot_config._PlotConfig__last_filter_args  # pylint: disable=W0212
    plot_config.filter_args = filter_args
    assert plot_config._PlotConfig__last_filter_args == filter_args  # pylint: disable=W0212
    assert plot_config.filter_args == filter_args
    plot_config.save()
    plot_config.refresh_from_db()
    assert not plot_config._PlotConfig__last_filter_args  # pylint: disable=W0212
    assert plot_config.filter_args == filter_args
    assert plot_config._PlotConfig__last_filter_args == filter_args  # pylint: disable=W0212


@pytest.mark.django_db
def test_plot_args():
    plot_config = PlotConfig.objects.create(description='plot_args_test',
                                            short_name='plot_args')
    plot_args = [{'linecolor': 'blue', 'title': 'testival'}]
    assert not plot_config._PlotConfig__last_plot_args  # pylint: disable=W0212
    plot_config.plot_args = plot_args
    assert plot_config._PlotConfig__last_plot_args == plot_args  # pylint: disable=W0212
    assert plot_config.plot_args == plot_args
    plot_config.save()
    plot_config.refresh_from_db()
    assert not plot_config._PlotConfig__last_plot_args  # pylint: disable=W0212
    assert plot_config.plot_args == plot_args
    assert plot_config._PlotConfig__last_plot_args == plot_args  # pylint: disable=W0212


@pytest.mark.django_db
def test_plot_annotations():
    plot_config = PlotConfig.objects.create(description='annotation_test',
                                            short_name='annotation')
    annotations = [{'mean': MeanAnnotation(),
                    'upper': UpperControlLimitAnnotation(),
                    'lower': LowerControlLimitAnnotation()}]
    assert not plot_config._PlotConfig__last_annotations  # pylint: disable=W0212
    plot_config.annotations = annotations
    assert plot_config._PlotConfig__last_annotations == annotations  # pylint: disable=W0212
    plot_config.save()
    plot_config.refresh_from_db()
    assert not plot_config._PlotConfig__last_annotations  # pylint: disable=W0212
    dummy = plot_config.annotations
    assert plot_config._PlotConfig__last_annotations  # pylint: disable=W0212
    for pl_anno, anno in zip(plot_config.annotations, annotations):
        assert pl_anno.keys() == anno.keys()
        for key in pl_anno:
            assert key in anno
            assert isinstance(pl_anno[key], type(anno[key]))


@pytest.mark.django_db
def test_plot_url(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_sample_characteristic_values()
    selenium = webdriver()
    try:
        selenium.get(live_server + '/plot/url/')
        login_as_admin(selenium)
        assert selenium.title == 'Page Not Found :('
        plot_config = PlotConfig.objects.create(description='url_test',
                                                short_name='url')
        plot_config.filter_args = [{'value__gt': 0.0}]
        plot_config.save()
        selenium.get(live_server + '/plot/url/')
        pull_session()
        assert selenium.find_element_by_class_name('bk-plot')
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_histogram(admin_client, live_server, webdriver, bokeh_server):
    create_correct_sample_data()
    create_sample_characteristic_values()
    create_plot_config()
    selenium = webdriver()
    selenium.implicitly_wait(10)
    try:
        selenium.get(live_server + '/plot/gt05/')
        login_as_admin(selenium)
        pull_session()
        assert len(selenium.find_elements_by_class_name('bk-plot')) == 2
        PlotConfig.objects.filter(short_name='gt05').update(histogram=False)
        selenium.get(live_server + '/plot/gt05/')
        assert len(selenium.find_elements_by_class_name('bk-plot')) == 1
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_index():
    create_limited_users()
    create_correct_sample_data()
    create_sample_characteristic_values()
    create_plot_config()
    multi = PlotConfig.objects.get(short_name='multi')
    generator = PlotGenerator(multi)
    plot_list = list(generator.plot_code_iterator())
    assert len(plot_list) == 2
    generator = PlotGenerator(multi, 0)
    plot_list = list(generator.plot_code_iterator())
    assert len(plot_list) == 1
    generator = PlotGenerator(multi, 1)
    plot_list = list(generator.plot_code_iterator())
    assert len(plot_list) == 1


@pytest.mark.django_db
def test_plot_titles():
    plot_config = PlotConfig.objects.create(short_name='dummy')
    plot_config.filter_args = []
    assert plot_config.titles == []
    plot_config.filter_args = [{}]
    assert plot_config.titles == ['']
    plot_config.titles = ['', '']
    assert plot_config.titles == ['']
    plot_config.titles = 'title'  # pylint: disable=R0204
    assert plot_config.titles == ['title']
    plot_config.titles = 'title|dummy'
    assert plot_config.titles == ['title']
    plot_config.filter_args = [{}, {}, {}]
    assert plot_config.titles == ['title', 'dummy', '']
    plot_config.titles = 'title|foo'
    assert plot_config.titles == ['title', 'foo', '']
    plot_config.titles = ['spam', 'egg']
    assert plot_config.titles == ['spam', 'egg', '']
    plot_config.titles = 'title|foo|bar'
    assert plot_config.titles == ['title', 'foo', 'bar']


@pytest.mark.django_db
def test_plot_create_product_config():
    create_correct_sample_data()
    assert PlotConfig.objects.all().count() == 3
    pcs = PlotConfig.objects.all()
    products = ['product1', 'product2', 'product3']
    titles = ['length', 'width', 'height']

    for index, prod in enumerate(products):
        assert pcs[index].short_name == prod
        assert pcs[index].titles == titles[:index + 1]
        assert len(pcs[index].filter_args) == index + 1
