.. DjConChart documentation master file, created by
   sphinx-quickstart on Sun Jul 10 14:17:36 2016.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.





Welcome to DjConChart's documentation!
======================================

DjConChart is a `Django <https://www.djangoproject.com/>`_ statistic process
control (SPC) server for small and middlesized companys.It allows you to create
interactive control charts for the browser and to manage your measurement data.
In the next releases an easy to use report generation for each measurement and
for the process will be added.
DjConChart is easy to integrate into your measurement software to automated the
measurement analysis.


Features
--------
* Storing of measurement data in a database
* Easy, django like filtering of the measurement data
* Creation of interactive control chart
* Calculation of characteristic values for the control chart out of raw data
* Version control of the calculation rules for the characteristic data
* Dashboard show always the latest measurements

Following Features
------------------
* Cross language API for importing measurement data
* Advanced reporting possibilities
* Cookbooks
* And many more

Overview
--------
.. toctree::
   :maxdepth: 2

   gettingstarted
   overview
   deployment
   api



.. _`gettingstarted`:

.. include:: gettingstarted.rst

.. _`Deployment`:

.. include:: deployment.rst




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


