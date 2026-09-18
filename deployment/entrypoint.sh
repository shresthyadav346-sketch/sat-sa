#!/bin/sh
set -e

DB_FILE="/app/data/sat_sa.db"

# Ensure data directory exists
mkdir -p /app/data

# If database doesn't exist or is empty, seed or generate it
if [ ! -f "$DB_FILE" ] || [ ! -s "$DB_FILE" ]; then
    if [ -f "/app/sat_sa_seed.db" ] && [ -s "/app/sat_sa_seed.db" ]; then
        echo "[*] Populating database from pre-built seed image..."
        cp /app/sat_sa_seed.db "$DB_FILE"
    else
        echo "[*] Generating synthetic SOC telemetry and running analytics pipeline..."
        python -m data_generator.generator
        python -m backend.app.services.analysis_runner
    fi
else
    echo "[*] Existing operational database detected at $DB_FILE."
fi

echo "[*] Starting SAT-SA Supervisory Platform on http://0.0.0.0:8000..."
exec python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
