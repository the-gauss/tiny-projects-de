# Python image with uv installed and os included
FROM ghcr.io/astral-sh/uv:python3.12-bookworm

# 1. Install OS tools (e.g., for pg_dump)
# We add libpq-dev because psycopg2 often needs it to compile.
RUN apt-get update && apt-get install -y postgresql-client-15 libpq-dev cron

# 2. Set a clean directory for your app
WORKDIR /app

# 3. Install the python env using uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# 4. Copy the script
COPY start.sh /app/
COPY elt/elt_script.py ./

# 5. Create a helper that cron can call
RUN printf '#!/bin/sh\ncd /app\nuv run python elt_script.py\n' > /usr/local/bin/run_elt.sh && \
    chmod +x /usr/local/bin/run_elt.sh

# 6. Register the cron job (3:00 AM UTC daily)
RUN printf 'SHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n0 3 * * * root /usr/local/bin/run_elt.sh >> /var/log/cron.log 2>&1\n' > /etc/cron.d/elt && \
    chmod 0644 /etc/cron.d/elt && \
    crontab /etc/cron.d/elt

# 7. Start cron in the foreground when the container launches
CMD ["cron", "-f"]
