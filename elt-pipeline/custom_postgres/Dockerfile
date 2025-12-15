FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    dbt-core==1.9.1 \
    dbt-postgres==1.9.1

WORKDIR /dbt

ENTRYPOINT ["dbt"]

