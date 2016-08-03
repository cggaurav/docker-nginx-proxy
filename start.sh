#!/bin/sh

python /tmp/setup.py --conf /etc/nginx/sites-enabled/automagic.conf --certs /etc/nginx/ssl/

echo "Generated config:"
echo "-----------------------------------------------------"
cat /etc/nginx/sites-enabled/automagic.conf
echo "-----------------------------------------------------"

echo "Starting NGINX..."
nginx
