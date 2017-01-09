FROM tutum/nginx
RUN rm /etc/nginx/sites-enabled/default
RUN rm /etc/nginx/sites-available/default
ADD sites-enabled/ /etc/nginx/sites-enabled
ADD sites-enabled/ /etc/nginx/sites-available
RUN mkdir /etc/nginx/conf/
ADD conf/uwsgi_params /etc/nginx/conf/uwsgi_params