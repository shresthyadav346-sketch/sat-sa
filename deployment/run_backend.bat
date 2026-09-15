@echo off
echo =========================================================================
echo   SAT-SA: Supervisory Analytics Tool for SOC Assessment
echo   Launching FastAPI Backend (100%% Offline / Air-Gapped Mode)
echo =========================================================================
cd /d "%~dp0\.."
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
pause
