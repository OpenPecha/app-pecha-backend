#!/bin/bash

# Start FastAPI development server with StatReload (slower but no permission issues)
# This uses polling instead of file system events
poetry run uvicorn pecha_api.app:api \
  --host 127.0.0.1 \
  --port 8000 \
  --reload \
  --reload-delay 2 \
  --use-colors
