FROM nginx:1.13.3


RUN rm /etc/nginx/conf.d/default.conf
COPY dash.conf /etc/nginx/conf.d/


COPY index.html /home/project/html/
