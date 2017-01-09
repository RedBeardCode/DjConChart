FROM tailordev/pandas:0.17.1
RUN apt-get update && apt-get install -y supervisor
RUN mkdir /app
RUN pip3 install django django-reversion django-crispy-forms django-pandas bokeh
RUN pip3 install psycopg2 uwsgi
COPY ./ /app/
COPY ./staticfiles/ /app/static/
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN mkdir /var/log/supervisord
RUN mkdir /var/log/uwsgi
CMD ["/usr/bin/supervisord"]
