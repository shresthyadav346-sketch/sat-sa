@echo off
echo =========================================================================
echo   SAT-SA: Supervisory Analytics Tool for SOC Assessment
echo   Smart India Hackathon (SIH) Prototype - Launching Full Suite
echo =========================================================================
cd /d "%~dp0\.."

start "SAT-SA Backend" cmd /k "python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000"
timeout /t 3 /nobreak >nul

start "SAT-SA Frontend" cmd /k "cd frontend && npm run dev -- --host 127.0.0.1 --port 5173"
timeout /t 2 /nobreak >nul

echo Launching browser at http://localhost:5173 ...
start http://localhost:5173
echo SAT-SA is now running! Keep the backend and frontend console windows open.
