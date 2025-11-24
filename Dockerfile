# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (if any needed, e.g. for postgres, but we use sqlite)
# RUN apt-get update && apt-get install -y --no-install-recommends ...

# Copy the requirements file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Collect static files
# For a simple setup, we can run this. 
# Note: In production, you might want to serve static files differently (e.g. Nginx, Whitenoise)
# For now, we'll assume Django can serve them or we use Whitenoise if added.
# Let's add a basic collectstatic command but it might fail if STATIC_ROOT is not set.
# We'll skip it for this simple dev/demo setup and rely on runserver or gunicorn if configured.
# Actually, for gunicorn to serve static files, we need Whitenoise or Nginx.
# To keep it simple and "containerized" without extra complexity, we will just run the app.
# If the user wants production ready, we'd add Whitenoise.
# Let's stick to the plan: gunicorn.
# We will expose port 8000
EXPOSE 8000

# Run gunicorn
CMD ["gunicorn", "RouteFinder.wsgi:application", "--bind", "0.0.0.0:8000"]
