#!/bin/sh

python /tmp/setup.py --conf /etc/nginx/sites-enabled/automagic.conf --certs /etc/nginx/ssl/

echo "Generated config:"
echo "-----------------------------------------------------"
cat /etc/nginx/sites-enabled/automagic.conf
echo "-----------------------------------------------------"

echo "Testing generated NGINX Config..."
nginx -t
if [ $? -eq 0 ]
then
  echo "Successful"
  echo ""

  echo "Starting NGINX..."
  nginx
else
  echo "Error"
fi
