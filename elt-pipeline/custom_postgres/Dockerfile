FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    dbt-core==1.9.1 \
    dbt-postgres==1.9.1

# Set a working directory for dbt projects within the container
WORKDIR /dbt

# ENTRYPOINT tells Docker to run `dbt` command by default when the container starts
ENTRYPOINT ["dbt"]

