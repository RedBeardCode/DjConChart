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
    server = None
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djcon_chart.settings")
    if 'createtestdata' in parameters:
        create_test_data()
    else:
        if 'runserver' in parameters and port_free():
            server = Popen(['bokeh', 'serve', '--log-level=warn',
                            '--allow-websocket-origin=localhost:8000',
                            '--allow-websocket-origin=127.0.0.1:8000']
                           )

        from django.core.management import execute_from_command_line
        execute_from_command_line(parameters)
        if server:
            server.terminate()

if __name__ == "__main__":
    manage_main(sys.argv)
