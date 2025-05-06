FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn supervisor

# Copy application code
COPY . .

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisord.conf

# Expose the Flask port (ensure it matches FLASK_PORT in your config)
EXPOSE 5000

# Run supervisord
CMD ["supervisord", "-c", "/etc/supervisord.conf"]