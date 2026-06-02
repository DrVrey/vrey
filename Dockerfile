FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p vrey_cache

EXPOSE 6666

ENV PYTHONUNBUFFERED=1
ENV PORT=6666

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:6666", "--workers", "1", "--threads", "4", "--timeout", "120"]
