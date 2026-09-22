FROM nousresearch/hermes-agent:latest

ENV HERMES_DASHBOARD=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends nginx gettext-base \
    && rm -rf /var/lib/apt/lists/*

COPY nginx.conf /etc/nginx/nginx.conf
COPY brn9-entry.sh /usr/local/bin/brn9-entry.sh
RUN chmod +x /usr/local/bin/brn9-entry.sh

COPY app/requirements.txt /srv/brn9/requirements.txt
RUN VIRTUAL_ENV=/opt/hermes/.venv uv pip install --no-cache-dir -r /srv/brn9/requirements.txt
COPY app/main.py /srv/brn9/main.py

CMD ["brn9-entry.sh"]