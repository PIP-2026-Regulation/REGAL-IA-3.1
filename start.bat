@echo off
echo Starting EU AI Act Compliance Advisor...
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv venv
    pause
    exit /b 1
)

REM Start backend in new window
echo Starting FastAPI backend...
start "EU AI Act Backend" cmd /k "venv\Scripts\activate.bat && python api.py"

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

REM Start frontend in new window
echo Starting React frontend...
start "EU AI Act Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:5173
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to exit...
pause > nul
