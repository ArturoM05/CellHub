# flask_payment_service/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copiar dependencias primero (cache de capas Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código fuente
COPY . .

EXPOSE 5000

# Gunicorn en producción (más robusto que el servidor de desarrollo de Flask)
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "app:app"]
