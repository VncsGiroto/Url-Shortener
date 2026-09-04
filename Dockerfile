FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY frontend/ ./frontend/
COPY wsgi.py ./
COPY migrations/ ./migrations/
COPY docker_entrypoint.sh ./
RUN chmod +x ./docker_entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./docker_entrypoint.sh"]
