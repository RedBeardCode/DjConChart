##########
DjConChart
##########

.. image:: https://travis-ci.org/RedBeardCode/DjConChart.svg?branch=master
    :target: https://travis-ci.org/RedBeardCode/DjConChart

.. image:: https://readthedocs.org/projects/djconchart/badge/?version=latest
    :target: http://djconchart.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status


DjConChart is a `Django <https://www.djangoproject.com/>`_ statistic process
control (SPC) server for small and middlesized companys.It allows you to create
interactive control charts for the browser and to manage your measurement data.
In the next releases an easy to use report generation for each measurement and
for the process will be added.
DjConChart is easy to integrate into your measurement software to automated the
measurement analysis.


********
Features
********
* Storing of measurement data in a database
* Easy, django like filtering of the measurement data
* Creation of interactive control chart
* Calculation of characteristic values for the control chart out of raw data
* Version control of the calculation rules for the characteristic data
* Dashboard show always the latest measurements

******************
Following Features
******************
* Cross language API for importing measurement data
* Advanced reporting possibilities
* Cookbooks
* And many more

***********
Quick Start
***********

* First download the source code and unzip to your test dir
* Install and create a virual enviroment with the following commands
    $ pip install --upgrade virtualenv
    $ virtualenv env
    $ source env/bin/activate
* Create the the database and admin user
    $ python manage.py makemigrations
    $ python manage.py migrate
    $ python manage.py createsuperuser
* Create test data
    $ python manage.py createtestdata
* Start the django development server
    $ python manage.py runserver
* Goto `Dashboard <http://127.0.0.1:8000/>`_ and login as one of the following
  users
  ** Admin user which you have created with createsuperuser
  ** Viewer (password: test) a readonly user
  ** Examiner (password: test) a user which is allowed to save new raw datas
  ** Manager (password: test) is allowed to add and change all objects
  ** Administrator (password: test) is allowed to add, change and delete all
     objects

.. ATTENTION::
    The django development server is NOT for productive use. Use it only to
    DjConChart. Have a look into django documentation for how to deploy
    DjConChart to a real server.

**********
Deployment
**********
Coming soon


******************
Commercial support
******************

This project is backed by RedBeardCode
If you need help implementing or hosting DjConChart, please contact us:
info@red-beard-code.de.
