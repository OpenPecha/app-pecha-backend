#!/bin/bash

# Start FastAPI development server with proper exclusions
poetry run uvicorn pecha_api.app:api \
  --host 127.0.0.1 \
  --port 8000 \
  --reload \
  --reload-exclude "local_setup/" \
  --reload-exclude ".git/" \
  --reload-exclude "__pycache__/" \
  --reload-exclude "*.pyc" \
  --reload-exclude ".venv/" \
  --reload-exclude "venv/" \
  --reload-exclude ".pytest_cache/" \
  --reload-exclude "*.log" 