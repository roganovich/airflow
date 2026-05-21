# Dockerfile for Apache Airflow with log_generator.py
FROM apache/airflow:2.10.4-python3.11

# Switch to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        curl \
        git \
        vim \
        wget \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Switch back to airflow user
USER airflow

# Set environment variables
ENV AIRFLOW_HOME=/opt/airflow
ENV AIRFLOW__CORE__LOAD_EXAMPLES=False
ENV AIRFLOW__CORE__EXECUTOR=LocalExecutor
ENV AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres/airflow
ENV AIRFLOW__WEBSERVER__SECRET_KEY=airflow_secret_key

# Copy requirements file if exists
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt || echo "No requirements.txt found, skipping"

# Copy log_generator.py and other project files
COPY log_generator.py ${AIRFLOW_HOME}/dags/log_generator.py
COPY scripts/ ${AIRFLOW_HOME}/scripts/

# Create directories for logs and data
RUN mkdir -p ${AIRFLOW_HOME}/logs ${AIRFLOW_HOME}/data

# Set working directory
WORKDIR ${AIRFLOW_HOME}

# Expose ports
EXPOSE 8080

# Default command
CMD ["standalone"]