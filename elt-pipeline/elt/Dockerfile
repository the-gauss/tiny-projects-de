FROM python:3.8-slim

# 1. Install OS tools (e.g., for pg_dump)
# We add libpq-dev because psycopg2 often needs it to compile
# triggers on docker-compose build
RUN apt-get update && apt-get install -y postgresql-client-15 libpq-dev

# 2. Set a clean directory for your app
WORKDIR /app

# 3. Copy requirements FIRST (Docker caches layers. If requirements don't change,
# it skips this slow step next time you build).
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the script
COPY elt_script.py .

# 5. Run - triggers on docker-compose up
CMD ["python", "elt_script.py"]