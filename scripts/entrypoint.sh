#!/bin/bash

# Airflow entrypoint script with custom initialization

set -e

echo "Starting Airflow initialization..."

# Initialize database if not already initialized
if [ ! -f "${AIRFLOW_HOME}/airflow.db" ]; then
    echo "Initializing Airflow database..."
    airflow db init
    
    echo "Creating admin user..."
    airflow users create \
        --username admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@example.com \
        --password admin
    
    echo "Database initialization complete."
else
    echo "Airflow database already exists, skipping initialization."
fi

# Upgrade database if needed
echo "Upgrading database..."
airflow db upgrade

# Create connections if needed
echo "Setting up Airflow connections..."

# Create a default PostgreSQL connection
airflow connections delete postgres_default 2>/dev/null || true
airflow connections add \
    postgres_default \
    --conn-type postgres \
    --conn-host postgres \
    --conn-login airflow \
    --conn-password airflow \
    --conn-port 5432 \
    --conn-schema airflow

# Create a default HTTP connection for API
airflow connections delete http_default 2>/dev/null || true
airflow connections add \
    http_default \
    --conn-type http \
    --conn-host https://api.example.com

echo "Airflow setup complete."

# Execute the main command
exec "$@"