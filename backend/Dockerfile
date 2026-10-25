FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast, lockfile-driven dependency installs
RUN pip install --no-cache-dir uv==0.8.17

# uv configuration:
# - copy files into the venv (avoids hardlink warnings across layers)
# - compile bytecode for faster container startup
# - place the venv OUTSIDE /app so the dev bind mount (./backend:/app in
#   docker-compose) does not shadow it at runtime
ENV UV_LINK_MODE=copy \
    UV_COMPILE_BYTECODE=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv

# Install dependencies from the lockfile in a cached layer.
# --frozen fails the build if the lock is out of date with pyproject.toml.
# Test tooling (the `dev` group) is included so `make test`, which runs
# pytest inside this container, keeps working.
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Put the project virtualenv on PATH so uvicorn/celery/alembic/pytest resolve
ENV PATH="/opt/venv/bin:$PATH"

# Copy application code
COPY . .

# Create a non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app /opt/venv
USER app

# Expose port
EXPOSE 8000

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
