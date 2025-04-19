#!/bin/sh

# Wait for the PostgreSQL database to be ready
echo "Waiting for PostgreSQL..."

while ! nc -z "$DB_HOST" "$DB_PORT"; do
  sleep 0.1
done

echo "PostgreSQL is up - continuing..."


# Run database migrations
python manage.py migrate
# python manage.py migrate --noinput

# Collect static files (optional, only if you need static files in production)
python manage.py collectstatic --noinput

# Start Gunicorn server with the correct settings module
# exec gunicorn collectionagency.wsgi:application --bind 0.0.0.0:8000

# Execute the command passed to the container
exec "$@"
