FROM python:3.13-slim

# pyswisseph is mixed C/C++: most files need gcc, one file (swhdbxx.cpp)
# needs g++. libsqlite3-0 is needed at runtime, libsqlite3-dev at build time.
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libsqlite3-0 \
    libsqlite3-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port $PORT"]
