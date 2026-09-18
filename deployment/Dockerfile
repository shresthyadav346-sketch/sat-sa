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

# Copy entrypoint script and ensure Unix line endings & executable permissions
COPY deployment/entrypoint.sh ./entrypoint.sh
RUN sed -i 's/\r$//' ./entrypoint.sh && chmod +x ./entrypoint.sh

# Create storage directory for database
RUN mkdir -p /app/data

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
