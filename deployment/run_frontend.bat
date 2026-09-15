@echo off
echo =========================================================================
echo   SAT-SA: Supervisory Analytics Tool for SOC Assessment
echo   Launching Frontend Dev Server
echo =========================================================================
cd /d "%~dp0\..\frontend"
npm run dev -- --host 127.0.0.1 --port 5173
pause
