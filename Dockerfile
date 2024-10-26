FROM python:3.12-slim

WORKDIR /app
ENV PYTHONPATH=/app

# Install required packages, including supervisord
RUN apt-get update && apt-get install -y \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy your project files
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app
COPY supervisord.conf /etc/supervisord.conf

# Use supervisord to start both services
CMD ["supervisord", "-c", "/etc/supervisord.conf"]
