Deployment
----------

Coming soon


Install uwsgi, nginx
Config uwsgi with uwsgi.ini and start it with uwsgi --ini uwsgi.ini
Config nginx with /etc/ngnix/site-aviable/djconchart and link it ln -s to /etc/ngnix/site-enable
add www-data to user group to allow permissions for socket (sudo adduser www-data vagrant)
install postgresql-server postgresql
change settings.py


set Hostname

hostnamectl set-hostname yourdjconchart.com

uwsgi --ini uwsgi.ini

uwsgi.ini

[uwsgi]
chdir=/home/vagrant/DjConChart
module=djcon_chart.wsgi:application
master=True
pidfile=/tmp/project-master.pid
vacuum=True
max-requests=5000
daemonize=/var/log/uwsgi/djcon_chart.log
socket=/home/vagrant/DjConChart/djcon_chart.sock
chmod-socket = 664
uid=www-data
gid=www-data
~




/etc/nginx/site-avaible/djconchart

server {
    listen 80;
    server_name yourdjconchart.com www.yourdjconchart.com;
    location /static/ {
        root /home/vagrant/DjConChart;
    }
    location / {
        include         uwsgi_params;
        uwsgi_pass      unix:/home/vagrant/DjConChart/djcon_chart.sock;
    }
    location /bokeh/ {
        proxy_pass http://127.0.0.1:5006;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host/bokeh;
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
        alias /usr/local/lib/python2.7/dist-packages/bokeh/server/static/;
    }
}
