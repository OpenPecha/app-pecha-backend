#!/bin/bash

# Start FastAPI development server without auto-reload
# Restart manually when you make changes
poetry run uvicorn pecha_api.app:api \
  --host 127.0.0.1 \
  --port 8000
