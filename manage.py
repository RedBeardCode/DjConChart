#!/usr/bin/env python
import os
import sys
from subprocess import Popen

from django.db.utils import OperationalError

from djcon_chart.wsgi import port_free


def create_test_data():
    '''
    Creates test data to play with the server
    '''
    from django import setup
    setup()
    from control_chart.tests.utilies import create_grouped_users
    from control_chart.tests.utilies import create_sample_characteristic_values
    from control_chart.tests.utilies import create_correct_sample_data
    from control_chart.tests.utilies import create_plot_config

    create_grouped_users()
    create_correct_sample_data()
    create_sample_characteristic_values()
    create_plot_config()

def run_test_server():
    try:
        from django import setup
        setup()

        #Only a Test if migration has be done.
        from control_chart.models import UserPlotSession
        dummy = UserPlotSession.objects.all().first()
    except OperationalError:
        manage_main(['', 'makemigrations', 'control_chart'])
        manage_main(['', 'migrate'])
        manage_main(['', 'createtestdata'])
    finally:
        manage_main(['', 'runserver'])

def manage_main(parameters):
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djcon_chart.settings")
    if 'createtestdata' in parameters:
        create_test_data()
    else:
        os.environ['BOKEH_LOAD_SERVER'] = ''

        from django.core.management import execute_from_command_line
        execute_from_command_line(parameters)

if __name__ == "__main__":
    manage_main(sys.argv)
