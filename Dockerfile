FROM python:3.11-slim

# Set environment variables for better python behavior
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for postgres and clean up
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Expose port
EXPOSE 8000

# Gunicorn handled in docker-compose command
CMD ["gunicorn", "RouteFinder.wsgi:application", "--bind", "0.0.0.0:8000"]
