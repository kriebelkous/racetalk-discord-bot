FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN useradd -m appuser && \
    chown -R appuser:appuser /app

RUN touch /app/trigger_signal && \
    chown appuser:appuser /app/trigger_signal && \
    chmod 664 /app/trigger_signal

COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

USER appuser

EXPOSE 5000

CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]