#!/usr/bin/env python
import os
import sys
from subprocess import Popen

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


if __name__ == "__main__":
    server = None
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djcon_chart.settings")
    if 'createtestdata' in sys.argv:
        create_test_data()
    else:
        if 'runserver' in sys.argv and port_free():
            server = Popen(['bokeh', 'serve', '--log-level=debug',
                            '--allow-websocket-origin=localhost:8000',
                            '--allow-websocket-origin=127.0.0.1:8000']
                           )

        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
        if server:
            server.terminate()
