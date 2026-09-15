# Multi-stage Dockerfile for 100% Offline SAT-SA Deployment

# Stage 1: Build React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci || npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Python Backend with Static Assets
FROM python:3.11-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABASE_URL="sqlite:////app/data/sat_sa.db"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, analytics, ml, and data generator
COPY backend/ ./backend/
COPY analytics/ ./analytics/
COPY ml/ ./ml/
COPY data_generator/ ./data_generator/

# Copy built frontend from stage 1 into frontend/dist
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Create storage directory for database
RUN mkdir -p /app/data

EXPOSE 8000

CMD ["sh", "-c", "python -m data_generator.generator && python -m backend.app.services.analysis_runner && python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000"]
