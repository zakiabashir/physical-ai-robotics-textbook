#!/bin/sh

echo "Starting FastAPI application..."
# Force main.py deployment with auth

# Check if PORT is set by Railway
if [ -z "$PORT" ]; then
    echo "WARNING: PORT not set, using Railway's dynamic port detection..."
    # Try to detect Railway's port from common environment variables
    PORT=${RAILWAY_PUBLIC_PORT:-${PORT:-8000}}
fi

echo "PORT detected: $PORT"
echo "HOST: ${HOST:-0.0.0.0}"
echo "Working directory: $(pwd)"

# Force PORT to be set (Railway sets it automatically)
export PORT=$PORT
export HOST=${HOST:-0.0.0.0}

echo "Final PORT: $PORT"
echo "Final HOST: $HOST"

# Try to run apps in order: main, main_rag, ai_main, simplified, simple
echo "Attempting to start main application with auth..."
if python -c "from app.main import app; print('Main app imported successfully')" 2>/dev/null; then
    echo "Main app import successful, starting uvicorn..."
    exec uvicorn app.main:app --host $HOST --port $PORT
elif python -c "from app.main_rag import app; print('RAG-enabled main app imported successfully')" 2>/dev/null; then
    echo "Main app failed, trying RAG-enabled app..."
    exec uvicorn app.main_rag:app --host $HOST --port $PORT
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