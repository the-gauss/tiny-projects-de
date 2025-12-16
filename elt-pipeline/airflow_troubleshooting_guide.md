# Airflow Pipeline Debugging Report

This document details the troubleshooting session for the `elt_and_dbt` pipeline. It covers five distinct issues encountered, their root causes, fixes, and general lessons for debugging Airflow DAGs.

## 1. Airflow 3 JWT Authentication Error

### The Issue
Immediately upon triggering the DAG, it failed with `403 Forbidden` and `InvalidSignatureError`.

### Root Cause
Airflow 3 introduced a new Execution API that requires JWT authentication between the triggerer/webserver and the execution workers. The environment variable `AIRFLOW__API_AUTH__JWT_SECRET` was missing. The old `AIRFLOW__API__SECRET_KEY` is not sufficient for this specific new auth mechanism.

### The Fix
Added `AIRFLOW__API_AUTH__JWT_SECRET` to `.env` and all Airflow services in `docker-compose.yaml`.

### General Lesson
**Authentication Changes:** Major version upgrades (Airflow 2 -> 3) often change security protocols. Always check the "Migration Guide" or "Breaking Changes" for required new environment variables when upgrading.

---

## 2. ELT Script Missing Environment Variables

### The Issue
The `run_elt_script` task failed with `CalledProcessError: exit status 1`.

### Root Cause
The Python script (`elt_script.py`) needed to connect to the database using `os.getenv('SRC_DB_NAME')`, etc. These variables existed in `.env` but were **not passed** to the `airflow-scheduler` container, which executes the `PythonOperator`.

### The Fix
Explicitly mapped the database variables (`SRC_DB_NAME`, `DEST_DB_NAME`, etc.) in the `airflow-scheduler` section of `docker-compose.yaml`.

### General Lesson
**Scheduler Context:** `PythonOperator` code runs *inside* the scheduler (or worker) container. It only sees environment variables available to that container. If your code needs external credentials, ensure they are passed to the Airflow service itself.

---

## 3. DBT Docker Mount Paths

### The Issue
The `run_dbt_models` task (`DockerOperator`) failed with:
`invalid mount config for type 'bind': invalid mount path: 'opt/dbt' mount path must be absolute`

### Root Cause
Docker requires absolute paths for volume mounts (e.g., `/opt/dbt`), but relative paths (`opt/dbt`) were provided in the DAG.

### The Fix
Updated `elt_dag.py` to use absolute paths:
```python
Mount(target='/opt/dbt', ...)  # Correct
Mount(target='opt/dbt', ...)   # Incorrect
```

### General Lesson
**Docker Volumes:** Always use absolute paths (starting with `/`) for both source and target in Docker volume mounts.

---

## 4. DBT Missing Environment Variables

### The Issue
The DBT container failed with `Env var required but not provided: 'DEST_DB_NAME'`.

### Root Cause
**Process Isolation:** The `DockerOperator` launches a *new, isolated container*. It does **not** inherit environment variables from the scheduler/worker that spawned it (unlike `PythonOperator` or `BashOperator`).

### The Fix
Explicitly passed the environment variables in the `DockerOperator` definition:
```python
DockerOperator(
    ...,
    environment={
        'DEST_DB_NAME': os.getenv('DEST_DB_NAME'),
        ...
    }
)
```

### General Lesson
**Operator Isolation:** Know your operator's execution environment:
- `PythonOperator`: Runs in the *current* container (inherits env).
- `DockerOperator` / `KubernetesPodOperator`: Runs in a *separate* container/pod (starts clean, needs explicit env vars).

---

## 5. Docker Network Isolation

### The Issue
The DBT container failed with `could not translate host name "destination_postgres"`.

### Root Cause
**Network Isolation:** By default, Docker containers started via `DockerOperator` use the default `bridge` network. The project's databases were on a custom network (`elt-pipeline_elt_network`). The DBT container couldn't "see" or resolve the hostnames of the databases.

### The Fix
Configured the operator to join the correct network:
```python
DockerOperator(
    ...,
    network_mode='elt-pipeline_elt_network'
)
```

### General Lesson
**Networking:** If your Airflow task spins up a container that needs to talk to other containers (like a DB), ensure they share a Docker network.

---

## Final Verification
We verified success by querying the destination database directly:
```bash
docker exec -i elt-pipeline-destination_postgres-1 psql -U thory -d dest_db -c "SELECT * FROM public.film_ratings LIMIT 5;"
```
Presence of data confirmed the full ELT + DBT pipeline executed correctly.
