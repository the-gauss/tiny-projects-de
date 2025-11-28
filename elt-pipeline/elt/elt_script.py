import subprocess
from dotenv import load_dotenv
import os
import time

load_dotenv()

def wait_for_postgres(host, max_retries=5, delay_seconds=5):
    """Wait for PostgreSQL to become available."""
    retries = 0
    while retries < max_retries:
        try:
            result = subprocess.run(
                ["pg_isready", "-h", host], check=True, capture_output=True, text=True)
            if "accepting connections" in result.stdout:
                print("Successfully connected to PostgreSQL!")
                return True
        except subprocess.CalledProcessError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            retries += 1
            print(
                f"Retrying in {delay_seconds} seconds... (Attempt {retries}/{max_retries})")
            time.sleep(delay_seconds)
    print("Max retries reached. Exiting.")
    return False

if not wait_for_postgres(host='source_postgres'):
    exit(1)

# COMPLETE FROM HERE ONWARDS IN THE DOTENV STYLE
print("Starting ELT script...")


def get_required_env(name: str) -> str:
    """Read a required environment variable, raising a clear error if missing."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set.")
    return value


# Configuration for the source PostgreSQL database, loaded from environment
source_config = {
    # These match the variable names used in docker-compose.yaml
    'dbname': get_required_env('SRC_DB_NAME'),
    'user': get_required_env('SRC_DB_USER'),
    'password': get_required_env('SRC_DB_PASS'),
    # Default to the service name from docker-compose as the hostname
    'host': os.getenv('SRC_DB_HOST', 'source_postgres'),
}

# Configuration for the destination PostgreSQL database, loaded from environment
destination_config = {
    'dbname': get_required_env('DEST_DB_NAME'),
    'user': get_required_env('DEST_DB_USER'),
    'password': get_required_env('DEST_DB_PASS'),
    'host': os.getenv('DEST_DB_HOST', 'destination_postgres'),
}

# Use pg_dump to dump the source database to a SQL file
dump_command = [
    'pg_dump',
    '-h', source_config['host'],
    '-U', source_config['user'],
    '-d', source_config['dbname'],
    '-f', 'data_dump.sql',
    '-w',  # Do not prompt for password
]

# Set the PGPASSWORD environment variable to avoid password prompt
subprocess_env = {**os.environ, 'PGPASSWORD': source_config['password']}

# Execute the dump command
subprocess.run(dump_command, env=subprocess_env, check=True)

# Use psql to load the dumped SQL file into the destination database
load_command = [
    'psql',
    '-h', destination_config['host'],
    '-U', destination_config['user'],
    '-d', destination_config['dbname'],
    '-a', '-f', 'data_dump.sql',
]

# Set the PGPASSWORD environment variable for the destination database
subprocess_env = {**os.environ, 'PGPASSWORD': destination_config['password']}

# Execute the load command
subprocess.run(load_command, env=subprocess_env, check=True)

print("Ending ELT script...")
