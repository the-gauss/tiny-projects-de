# Python image with uv installed and os included
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# 1. Install OS tools (e.g., for pg_dump)
# We add libpq-dev because psycopg2 often needs it to compile.
RUN apt-get update && apt-get install -y postgresql-client-15 libpq-dev

# 2. Set a clean directory for your app
WORKDIR /app

# 3. Install the python env using uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 4. Copy the script
COPY elt/elt_script.py ./

# 5. Run - triggers on docker-compose up
CMD ["uv", "run", "python", "elt_script.py"]
