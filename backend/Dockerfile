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

# Deploy flexible standalone authentication server V3
# Handles both JSON and form-encoded data with chat and Google OAuth
CMD ["uvicorn", "app.standalone_full_v3:app", "--host", "0.0.0.0", "--port", "8080"]
