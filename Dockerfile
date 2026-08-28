FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY wsgi.py ./
COPY migrations/ ./migrations/

EXPOSE 8000

CMD ["sh", "-c", "flask --app wsgi db upgrade && flask --app wsgi run --host=0.0.0.0 --port=8000"]
