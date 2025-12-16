from datetime import datetime, timedelta
from airflow import DAG
from docker.types import Mount
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.providers.docker.operators.docker import DockerOperator
import subprocess
import os


# These will be the default arguments for the DAG we create later
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
}

def run_elt_script():
    """Function to run the ELT script inside a Docker container."""
    script_path = '/opt/airflow/elt/elt_script.py'

    # Args: check=True will raise an error if the command fails; capture_output=True captures stdout/stderr; text=True returns output as string
    result = subprocess.run(
        ['python', script_path], check=True, capture_output=True, text=True
        )
    
    if result.returncode != 0:
        raise RuntimeError(f"ELT script failed with error: {result.stderr}")
    print(f"ELT script output: {result.stdout}")

# Args: catchup=False ensures that only the latest DAG run is executed
# A DAG is a collection of all the tasks you want to run, organized in a way that reflects their relationships and dependencies.
dag = DAG(
    'elt_and_dbt',
    default_args=default_args,
    description='A DAG to run ELT and DBT tasks',
    start_date=datetime(2025, 12, 15),
    catchup=False,
)


# Task 1: Because it's a Python function, we use PythonOperator
# A "task" in Airflow is a single unit of work; here, it's running the ELT script. It consists of of a callable function and its parameters, and the DAG it belongs to.
t1 = PythonOperator(
    task_id='run_elt_script',
    python_callable=run_elt_script,
    dag=dag,
)

# We did not use a dbt image, but built one from our Dockerfile.dbt, so we use DockerOperator as below
# Task 2: Run DBT models using DockerOperator
t2 = DockerOperator(
    task_id='run_dbt_models',
    image='elt-pipeline-dbt:latest',  # This should match the image name built from Dockerfile.dbt
    command=[
        'run',
        '--profiles-dir', 'root/.dbt',  # Path inside the container where profiles.yml is located
        '--project-dir', '/dbt',  # Path inside the container where dbt project is located
    ],
    auto_remove='success',
    docker_url='unix://var/run/docker.sock',  # Use the Docker socket to run the container
    network_mode='bridge',  # Use bridge network to allow communication between containers
    mounts=[
        Mount(source='/Users/thory/tiny-projects/tiny-projects-de/elt-pipeline/custom_postgres', # The mounts are the same volume mappings as in docker-compose.yaml for dbt.
              target='opt/dbt', type='bind'),
        Mount(source='/Users/thory/.dbt',
              target='root/.dbt', type='bind'),
    ],
    dag=dag,
)

# Order of execution: t1 (ELT) must run before t2 (DBT)
t1 >> t2

# In t1 and t2, Airflow "CREATES" the two services, and runs them as per the defined order.
# We now do no need them to be defined in docker-compose.yaml, as Airflow will handle their lifecycle.