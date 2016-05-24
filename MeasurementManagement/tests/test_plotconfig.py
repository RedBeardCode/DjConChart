import pytest

from MeasurementManagement.models import PlotConfig
from MeasurementManagement.plot_annotation import MeanAnnotation, UpperInterventionAnnotation, \
    LowerInterventionAnnotation
from MeasurementManagement.plot_util import PlotGenerator
from MeasurementManagement.plot_util import pull_session
from MeasurementManagement.tests.utilies import login_as_admin, create_correct_sample_data, \
    create_sample_characteristic_values, create_plot_config, create_limited_users


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
    annotations = [{'mean': MeanAnnotation(),
                   'upper': UpperInterventionAnnotation(),
                    'lower': LowerInterventionAnnotation()}]
    assert not plot_config._PlotConfig__last_annotations
    plot_config.annotations = annotations
    assert plot_config._PlotConfig__last_annotations == annotations
    plot_config.save()
    plot_config.refresh_from_db()
    assert not plot_config._PlotConfig__last_annotations
    dummy = plot_config.annotations
    assert plot_config._PlotConfig__last_annotations
    for pl_anno, anno in zip(plot_config.annotations, annotations):
        assert pl_anno.keys() == anno.keys()
        for key in pl_anno:
            assert key in anno
            assert type(pl_anno[key]) == type(anno[key])


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
            assert selenium.find_element_by_class_name('bk-plot')
        except IOError:
            # no bokeh server running
            assert selenium.find_element_by_tag_name('body').text == 'Server Error (500)'
    finally:
        selenium.quit()


@pytest.mark.django_db
def test_plot_histogram(admin_client, live_server, webdriver):
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
    except IOError:
        # no bokeh server running
        assert selenium.find_element_by_tag_name('body').text == 'Server Error (500)'
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
    plot_list = list(generator.create_plot_code_iterator())
    assert len(plot_list) == 2
    generator = PlotGenerator(multi, 0)
    plot_list = list(generator.create_plot_code_iterator())
    assert len(plot_list) == 1
    generator = PlotGenerator(multi, 1)
    plot_list = list(generator.create_plot_code_iterator())
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
    plot_config.titles = 'title'
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
