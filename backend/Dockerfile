FROM python:3.9.16-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /code
COPY . .

## Setup commands
RUN python3 -m venv env
RUN source env/bin/activate
RUN python scripts/export_env.py
RUN sh scripts/install_dependencies.sh
RUN sh scripts/migrations.sh