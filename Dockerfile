# Etapa 1 — compilar frontend React + Polaris
FROM node:20-alpine AS frontend-build
WORKDIR /app
COPY frontend/ ./frontend/
RUN cd frontend && npm install && npm run build

# Etapa 2 — Django
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend-build /app/static/frontend ./static/frontend

EXPOSE 8000
