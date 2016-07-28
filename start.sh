#!/bin/sh

env >/tmp/env.txt
# cat /tmp/env.txt

# echo "====================================================="
# echo "SSL"
# echo "====================================================="

echo ${SERVER_CRT} >/etc/nginx/ssl/server.crt
echo ${SERVER_KEY} >/etc/nginx/ssl/server.key

if [ -n "${SERVER_KEY}" ]; then
  echo "SSL Certificate written: /etc/nginx/ssl/server.crt"
fi

if [ -n "${SERVER_CRT}" ]; then
  echo "SSL Key written: /etc/nginx/ssl/server.key"
fi

if [ -n "${SERVER_KEY}" ]; then
  if [ -n "${SERVER_CRT}" ]; then
    echo "SSL Enabled."
    # cat /etc/nginx/ssl/server.crt
    # cat /etc/nginx/ssl/server.key
  fi;
fi;

# echo "====================================================="
# echo "Detected links"
# echo "====================================================="

cat /tmp/env.txt | gawk 'match($0, /^([A-Z0-9_]+)_([0-9]+)_ENV_VIRTUAL_HOST=(.*)/, a) { print tolower(a[1]) " 0HOST " a[3] }' | uniq >/tmp/data.txt
cat /tmp/env.txt | gawk 'match($0, /^([A-Z0-9_]+)_([0-9]+)_PORT_[0-9]+_TCP+=tcp:\/\/(.+)$/, a) { print tolower(a[1]) " 1LINK " a[3] }' | uniq >>/tmp/data.txt
cat /tmp/data.txt | sort >/tmp/data2.txt
# cat /tmp/data2.txt

# cat /tmp/env.txt | gawk 'match($0, /^([A-Z0-9_]+)_([0-9]+)_PORT=/, a) { print tolower(a[1]) }' | uniq >/tmp/linknames.txt
# cat /tmp/links.txt

# echo "====================================================="
# echo "Grouping links to sites"
# echo "====================================================="
# cat /tmp/links.txt | awk -F " " '{ x[$1] = x[$1] " " $3 } END { for(k in x) { print "/tmp/makesite.sh " k x[k] } }' >/tmp/genmakesites.sh
cat /tmp/data2.txt | awk -F " " '{ x[$1] = x[$1] " " $3 } END { for(k in x) { print "./tmp/makesite.sh " k x[k] } }' >/tmp/genmakesites.sh
# cat /tmp/genmakesites.sh
chmod +x /tmp/genmakesites.sh

# echo "====================================================="
# echo "Generating site-files..."
# echo "====================================================="
./tmp/genmakesites.sh >/etc/nginx/sites-enabled/automagic.conf

echo "Generated config:"
echo "-----------------------------------------------------"
cat /etc/nginx/sites-enabled/automagic.conf
echo "-----------------------------------------------------"

# echo "====================================================="
echo "Starting NGINX..."
# echo "====================================================="
nginx
