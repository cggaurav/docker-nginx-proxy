#!/bin/bash

echo "# Make site"
echo "# All args $@ "

NAME=$1
shift

URLS=`echo $1 | sed -e 's/,/ /g'`
shift

if [ "$#" -lt 1 ]; then
    echo "# Illegal number of parameters"
    exit 1
fi

echo "# Site ID ${NAME} "
echo "# Site URLS ${URLS} "
echo ""

echo "upstream ${NAME}-origin {"
while test ${#} -gt 0
do
  if [[ ! $1 =~ ":443" ]]; then
    echo "  server $1;"
  fi
  shift
done
echo "}"
echo ""

echo "server {"
echo "  listen 80;"
echo "  server_name ${URLS};"
echo "  location / {"
echo "    proxy_pass http://${NAME}-origin;"
echo "    proxy_set_header Host \$host;"
echo "    proxy_set_header X-Forwarded-For \$remote_addr;"
echo "    proxy_next_upstream_timeout 3s;"
echo "    proxy_read_timeout 10s;"
echo "    proxy_send_timeout 10s;"
echo "  }"
echo "}"
echo ""

if [ -n "${SERVER_KEY}" ]; then
  if [ -n "${SERVER_CRT}" ]; then
    echo "server {"
    echo "  listen 443;"
    echo "  server_name ${URLS};"
    echo "  ssl on;"
    echo "  ssl_certificate /etc/nginx/ssl/server.crt;"
    echo "  ssl_certificate_key /etc/nginx/ssl/server.key;"
    echo "  location / {"
    echo "    proxy_pass http://${NAME}-origin;"
    echo "    proxy_set_header Host \$host;"
    echo "    proxy_set_header X-Forwarded-For \$remote_addr;"
    echo "    proxy_next_upstream_timeout 3s;"
    echo "    proxy_read_timeout 10s;"
    echo "    proxy_send_timeout 10s;"
    echo "  }"
    echo "}"
    echo ""
  fi
fi
