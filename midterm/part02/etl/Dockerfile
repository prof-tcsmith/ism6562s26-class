FROM python:3.11-slim

RUN apt-get update && apt-get install -y cron && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir psycopg2-binary

WORKDIR /app

COPY etl_script.py .
COPY crontab /etc/cron.d/etl-cron
COPY entrypoint.sh .

RUN chmod 0644 /etc/cron.d/etl-cron && \
    crontab /etc/cron.d/etl-cron && \
    chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
