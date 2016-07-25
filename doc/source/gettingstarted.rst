

Getting started
---------------

* First download the source code and unzip to your test dir

* Install and create a virual enviroment with the following commands
    .. code:: bash

        $ pip install --upgrade virtualenv
        $ virtualenv env
        $ source env/bin/activate

* Create the the database and admin user
    .. code:: bash

        $ python manage.py makemigrations
        $ python manage.py migrate
        $ python manage.py createsuperuser

* Create test data
    .. code:: bash

        $ python manage.py createtestdata

* Start the django development server
    .. code:: bash

        $ python manage.py runserver

* Goto `Dashboard <http://127.0.0.1:8000/>`_ and login as one of the following
  users

  * Admin user which you have created with createsuperuser

  * Viewer (password: test) a readonly user

  * Examiner (password: test) a user which is allowed to save new raw datas

  * Manager (password: test) is allowed to add and change all objects

  * Administrator (password: test) is allowed to add, change and delete all
    objects


.. ATTENTION::
    The django development server is NOT for productive use. Use it only to
    DjConChart. Have a look into django documentation for how to deploy
    DjConChart to a real server.
