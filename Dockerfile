FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
# RUN apt-get update && apt-get install -y \
#     libpq-dev gcc netcat && \
#     rm -rf /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y \
    libpq-dev gcc netcat-openbsd && \
    rm -rf /var/lib/apt/lists/*


# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the application code
COPY . .

# Expose the default Django port
EXPOSE 8000

# Copy the entrypoint script
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/entrypoint.sh"]

# Default command to run the app with Gunicorn
CMD ["gunicorn", "collectionagency.wsgi:application", "--bind", "0.0.0.0:8000"]
