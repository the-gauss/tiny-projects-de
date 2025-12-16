FROM apache/airflow:3.1.5

RUN pip install apache-airflow-providers-docker

# We are using uv for all other services, but the `apache/airflow` image is a fully managed images that 
# ships with Airflow and all its dependencies pre-installed. Using uv would mean using a uv managed Python image
# and then installing Airflow and all its dependencies manually, which is more complex and error-prone.
# This is an exception, and for rest ofthe services, we shall still consider uv as superior for dependency management

# Also, unlike other services (dbt and all), most teams run Airflow inside containers even during development,
# because it mirrors production and bundles all dependencies. Running it natively on local machine is rarely necessary for 99% use cases.
