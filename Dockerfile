FROM kyma/docker-nginx

RUN apt-get -y update
RUN apt-get -y install gawk

ADD sites-enabled/* /etc/nginx/sites-enabled/
ADD start.sh /tmp/
ADD makesite.sh /tmp/
ADD nginx.conf /etc/nginx/

EXPOSE 80
EXPOSE 443

CMD '/tmp/start.sh'
