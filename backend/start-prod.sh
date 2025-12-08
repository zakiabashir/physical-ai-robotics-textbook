#!/bin/bash

echo "Starting Physical AI Textbook Backend (Production)..."
echo "==============================================="

# Set production environment
export ENVIRONMENT=production
export DEBUG=false

# Check if required environment variables are set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "ERROR: GEMINI_API_KEY environment variable not set"
    exit 1
fi

if [ -z "$SECRET_KEY" ]; then
    echo "ERROR: SECRET_KEY environment variable not set"
    exit 1
fi

# Start the application
echo "Starting production server on port 8000..."
exec gunicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --worker-connections 100 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --timeout 60 \
    --keep-alive 2 \
    --access-logfile - \
    --error-logfile - \
    --log-level info