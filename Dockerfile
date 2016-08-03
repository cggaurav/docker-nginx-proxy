FROM kyma/docker-nginx

RUN apt-get -y update
RUN apt-get -y install curl gawk python

ADD sites-enabled/* /etc/nginx/sites-enabled/
ADD start.sh /tmp/
ADD setup.py /tmp/
ADD makesite.sh /tmp/
ADD nginx.conf /etc/nginx/
ADD sites.conf.tmpl /etc/docker-gen/

EXPOSE 80
EXPOSE 443

CMD '/tmp/start.sh'
