#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Setup script for DjConChart.
After install the package you can use the command

djconchart_testserver

to instance of the django dev server with test data for DjConChart to see how
DjConChart works.
"""
from os import listdir, sep

from os.path import isfile
from setuptools import setup
from pip.req import parse_requirements


def get_files_in_dir(path):
    """
    Return a list of filenames in a directory
    """
    def filepath(path, filename):
        """
        Creates full file path with path and filename
        """
        return path + sep + filename
    return (path,
            [filepath(path, lfi) for lfi in listdir(path)
             if isfile(filepath(path, lfi))])


INSTALL_REPS = parse_requirements('requirements.txt', session=False)

REPS = [str(ir.req) for ir in INSTALL_REPS]


setup(name='DjConChart',
      version='0.1',
      description='DjConChart is a Django based statistic '
                  'process control (SPC) server',
      author='RedBeardCode',
      author_email='s.farmbauer@red-beard-code.de',
      url='https://github.com/RedBeardCode/DjConChart',
      packages=['djcon_chart', 'control_chart', 'control_chart.tests'],

      py_modules=['manage', 'conftest'],
      install_requires=REPS,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: System Administrators',
          'License :: OSI Approved :: Python Software Foundation License',
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python',
      ],
      entry_points={'console_scripts':
                    ['djconchart_test = manage:run_test_server']},
      data_files=[get_files_in_dir('templates'),
                  get_files_in_dir('control_chart/templates'),
                  get_files_in_dir('samples_rsc'),
                  get_files_in_dir('static/css'),
                  get_files_in_dir('static/css/images'),
                  get_files_in_dir('static/fonts'),
                  get_files_in_dir('static/js'),
                  get_files_in_dir('static/js/vendor'),
                  get_files_in_dir('static/js/vendor/snippets'), ])
