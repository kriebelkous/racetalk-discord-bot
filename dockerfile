# Use Python 3.11 slim base image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy project files
COPY . .

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user
RUN useradd -m appuser && \
    mkdir -p /app/logs /app/run && \
    chown -R appuser:appuser /app

# Optionally pre-create trigger_signal
RUN touch /app/trigger_signal && \
    chown appuser:appuser /app/trigger_signal && \
    chmod 664 /app/trigger_signal

# Copy Supervisor config
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Switch to non-root user
USER appuser

# Expose Flask port
EXPOSE 5000

# Run Supervisor
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]