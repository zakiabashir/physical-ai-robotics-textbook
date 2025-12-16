FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ \
    && pip install --no-cache-dir --upgrade pip \
    && apt-get remove -y gcc g++ \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x start.sh

RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app

USER app

ENV HOST=0.0.0.0
ENV PORT=8000

# Railway injects its own PORT anyway
# EXPOSE optional

# Switch to main_auth_only.py with authentication
CMD ["sh", "-c", "uvicorn app.main_auth_only:app --host $HOST --port $PORT"]
