Deployment
==========

To use DjConChart in production you have to deploy it on a server. You can use
every WebServer and database which Django works with. As an Example I used the
combination of nginx and Postgresql on an ubuntu linux server. But I should also
work an every other linux distribution as well as on MacOs or Windows. For a
deployment tutorial for MacOs or Windows I would be really thankful.


Installing requirements
-----------------------

First all requiered software packages have to be install. On ubuntu I used apt-get
to install none python software and pip to install python software. Of course pip
is avaiable on all plattform but for installing the none python software use the
package manager of your system.
Replace the version of the postgresql-server-dev-X.Y to the one which is avaiable
on your system.

    .. code-block:: bash

        $ sudo apt-get install python-dev python-pip nginx postgresql postgresql-server-dev-X.Y



Configure database
------------------
After installing postgresql we have to create a database and a datebase user for
DjConchart. Therefore execute the following command in the terminal. Replace
DJCONCHART_USER with the your user which runs DjConChart.

    .. code-block:: bash

        $ sudo su - postgres
        $ psql
        $ CREATE DATABASE djconchart;
        $ CREATE USER djconchart_user WITH PASSWORD 'password';
        $ GRANT ALL PRIVILEGES ON DATABASE djconchart TO djconchart_user;
        $ \q
        $ exit

Installing DjConChart
---------------------

The easiest way to install the latest version of DjConChart is to clone the github
repository. Therefore you need to install git.

    .. code-block:: bash

        $ sudo apt-get install git
        $ git clone https://github.com/RedBeardCode/DjConChart.git
        $ cd DjConChart/

You also can download a zip archive of the latest version from the github page and
unpack it in your working directory.
After you got the source code of DjConChart you have to install the required python
packages with pip.

    .. code-block:: bash

        $ sudo pip install -r requirements.txt

Add the IP address of your server to the ALLOWED_HOSTS in the djconchart/settings.py file.

    .. code-block:: python

        ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'SERVER_IP']


Set the some environment variables to define your instance.

        .. code-block:: bash

                SECRET_KEY="YourSecurityKey"
                DB_USER="Username of your db user"
                DB_PASS="Password of your db user"
                DB_NAME="Database name"
                DB_SERVICE="Hostname of the db"
                DB_PORT="DB Port"

If the database is configured correct you can create the database tables for the
project with the following commands.

    .. code-block:: bash

        python manage.py makemigrations control_chart
        python manage.py migrate


Configure webserver
-------------------

To inform all server components about the url of your server we simply set the
hostname of the machine to the used url.

    .. code-block:: bash

        sudo hostnamectl set-hostname yourdjconchart.com

Uwsgi provides the DjConChart to nginx over a socket and writes a log file in
/var/log/uwsgi/. To make this possible we have to set some user permissions.

    .. code-block:: bash

        sudo adduser www-data DJCONCHART_USER
        sudo mkdir /var/log/uwsgi
        sudo chown DJCONCHART_USER /var/log/uwsgi/



Nginx is configured over the /etc/nginx/site-avaible/djconchart config file.
Replace PATH_TO_DJCONCHART with your working directory.

    .. code-block:: nginx

        server {
            listen 80;
            server_name $hostname;
            location /static/ {
                root PATH_TO_DJCONCHART;
            }
            location / {
                include         uwsgi_params;
                #Replace with your DjConChart directory
                uwsgi_pass      unix:PATH_TO_DJCONCHART/djcon_chart.sock;
            }
            location /bokeh/ {
                proxy_pass http://127.0.0.1:5006;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_http_version 1.1;
                proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
                proxy_set_header Host $server_name/bokeh;
                proxy_buffering off;
                rewrite /bokeh/(.*) /$1 break;
            }
            location /ws {
                proxy_pass http://127.0.0.1:5006;
                proxy_set_header Upgrade $http_upgrade;
                proxy_set_header Connection "upgrade";
                proxy_http_version 1.1;
            }


            location /bokeh/static/ {
                #Location of the static files of the bokeh server. This can differ on your system
                alias /usr/local/lib/python2.7/dist-packages/bokeh/server/static/;
            }
        }

And to enable the site you have to set the following symbolic link.

    .. code-block:: bash

        sudo ln -s /etc/nginx/sites-avaible/djconchart /etc/nginx/sites-enabled/default




Configure uwsgi with uwsgi.ini file in your DjConChart directory. Replace PATH_TO_DJCONCHART with your working directory.



    .. code-block:: INI

        [uwsgi]
        chdir=PATH_TO_DJCONCHART
        module=djcon_chart.wsgi:application
        master=True
        pidfile=/tmp/project-master.pid
        vacuum=True
        max-requests=5000
        daemonize=/var/log/uwsgi/djcon_chart.log
        socket=PATH_TO_DJCONCHART/djcon_chart.sock
        chmod-socket = 664
        uid=www-data
        gid=www-data

Now you can start uwsgi.

    .. code-block:: bash

        $ uwsgi --ini uwsgi.ini











~




