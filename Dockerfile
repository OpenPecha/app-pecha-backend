# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    meson \
    gtk-doc-tools \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the pyproject.toml and poetry.lock files to the container
COPY pyproject.toml poetry.lock /app/

# Install Poetry and Python dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copy the rest of the application code to the container
COPY . /app

# Expose the port that the app runs on
EXPOSE 8000

# Command to run the application
CMD ["sh", "-c", "poetry run alembic stamp head && poetry run alembic upgrade head && poetry run uvicorn pecha_api.app:api --host 0.0.0.0 --port 8000"]

# # Use the official Python image from the Docker Hub
# FROM python:3.12-slim

# # Set the working directory in the container
# WORKDIR /app

# # Copy the pyproject.toml and poetry.lock files to the container
# COPY pyproject.toml poetry.lock /app/

# RUN pip install poetry && \
#     poetry config virtualenvs.create false && \
#     poetry install --no-root

# # Copy the rest of the application code to the container
# COPY . /app

# # Expose the port that the app runs on
# EXPOSE 8000

# # Command to run the application
# CMD ["sh", "-c", "poetry run alembic stamp head && poetry run alembic upgrade head && poetry run uvicorn pecha_api.app:api --host 0.0.0.0 --port 8000"]