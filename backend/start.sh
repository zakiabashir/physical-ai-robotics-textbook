#!/bin/sh

echo "Starting FastAPI application..."
echo "PORT: ${PORT}"
echo "HOST: ${HOST:-0.0.0.0}"
echo "Working directory: $(pwd)"
echo "Listing files:"
ls -la

# Set default port if not provided
PORT=${PORT:-8000}
HOST=${HOST:-0.0.0.0}

echo "Final PORT: $PORT"
echo "Final HOST: $HOST"

# Try to run apps in order: main, ai_main, simplified, simple
echo "Attempting to start main application..."
if python -c "from app.main import app; print('Main app imported successfully')" 2>/dev/null; then
    echo "Main app import successful, starting uvicorn..."
    exec uvicorn app.main:app --host $HOST --port $PORT
elif python -c "from ai_main import app; print('AI Enhanced app imported successfully')" 2>/dev/null; then
    echo "Main app failed, starting AI enhanced app..."
    exec uvicorn ai_main:app --host $HOST --port $PORT
elif python -c "from app.main_simplified import app; print('Simplified app imported successfully')" 2>/dev/null; then
    echo "AI app failed, starting simplified app..."
    exec uvicorn app.main_simplified:app --host $HOST --port $PORT
else
    echo "All apps failed, starting minimal app..."
    exec uvicorn simple_main:app --host $HOST --port $PORT
fi