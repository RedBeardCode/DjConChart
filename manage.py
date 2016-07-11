#!/usr/bin/env python
import os
import sys
from subprocess import Popen

def port_free(port=5006):
    '''
    Checks if the port for the bokeh server is in use
    '''
    import socket;
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('127.0.0.1', port))
    return result != 0;

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
            server = Popen(['bokeh', 'serve',
                            '--allow-websocket-origin=localhost:8000',
                            '--allow-websocket-origin=127.0.0.1:8000']
                           )

        from django.core.management import execute_from_command_line
        execute_from_command_line(sys.argv)
        if server:
            server.terminate()
