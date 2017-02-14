#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Django manage.py to control the project
"""

import os
import sys

from django.db.utils import OperationalError


def create_test_data():
    '''
    Creates test data to play with the server
    '''
    from django import setup
    setup()
    from control_chart.tests.utilies import create_grouped_users
    from control_chart.tests.utilies import create_characteristic_values
    from control_chart.tests.utilies import create_correct_sample_data
    from control_chart.tests.utilies import create_plot_config

    create_grouped_users()
    create_correct_sample_data()
    create_characteristic_values()
    create_plot_config()


def run_test_server():
    """
    Run the development server
    """
    try:
        from django import setup
        setup()

        # Only a Test if migration has be done.
        from control_chart.models import UserPlotSession
        dummy = UserPlotSession.objects.all().first()
    except OperationalError:
        manage_main(['', 'makemigrations', 'control_chart'])
        manage_main(['', 'migrate'])
        manage_main(['', 'createtestdata'])
    finally:
        manage_main(['', 'runserver'])


def manage_main(parameters):
    """
    Manage the project
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djcon_chart.settings")
    if 'createtestdata' in parameters:
        create_test_data()
    else:
        os.environ['BOKEH_LOAD_SERVER'] = 'http://localhost:8000/bokeh/'

        from django.core.management import execute_from_command_line
        execute_from_command_line(parameters)


if __name__ == "__main__":
    manage_main(sys.argv)
