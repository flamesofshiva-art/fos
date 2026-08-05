FROM python:3.13-slim

# pyswisseph needs libsqlite3 at runtime -- Railway's default slim images
# don't include it, which causes "ImportError: libsqlite3.so.0" on startup.
RUN apt-get update && apt-get install -y --no-install-recommends \
    libsqlite3-0 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT
