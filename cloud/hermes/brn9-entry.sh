#!/bin/sh
set -e
export PATH="/opt/hermes/.venv/bin:$PATH"

(
    cd /srv/brn9
    exec uvicorn main:app --host 127.0.0.1 --port 8000
) &

envsubst '${PORT}' < /etc/nginx/nginx.conf > /tmp/nginx.conf
mkdir -p /tmp/nginx/body /tmp/nginx/proxy /tmp/nginx/fastcgi /tmp/nginx/uwsgi /tmp/nginx/scgi
exec nginx -c /tmp/nginx.conf -g 'daemon off;'