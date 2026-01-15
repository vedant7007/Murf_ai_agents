@echo off
cls
echo ========================================
echo   REALM OF VROSKIT - Quick Start
echo ========================================
echo.

echo Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker not found!
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    echo.
    echo Alternatively, download LiveKit server binary from:
    echo https://github.com/livekit/livekit/releases
    pause
    exit /b 1
)

echo.
echo [1/3] Starting LiveKit Server...
echo ========================================
start "LiveKit Server" cmd /k "echo Starting LiveKit Server... && docker run --rm -p 7880:7880 -p 7881:7881 -p 7882:7882/udp livekit/livekit-server --dev"

echo Waiting for LiveKit server to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/3] Starting Backend Agent...
echo ========================================
cd ten-days-of-voice-agents-2025\backend
if not exist ".venv" (
    echo ERROR: Virtual environment not found!
    echo Run: python -m venv .venv
    cd ..\..
    pause
    exit /b 1
)
start "Backend Agent" cmd /k "echo Starting Game Master Agent... && .venv\Scripts\activate && python src/agent.py dev"
cd ..\..

echo Waiting for agent to initialize...
timeout /t 3 /nobreak >nul

echo.
echo [3/3] Starting Frontend...
echo ========================================
cd ten-days-of-voice-agents-2025\frontend
start "Frontend Server" cmd /k "echo Starting Frontend... && npm run dev"
cd ..\..

echo.
echo ========================================
echo   ALL SERVICES STARTED!
echo ========================================
echo.
echo  LiveKit Server: http://localhost:7881
echo  Frontend:       http://localhost:3000
echo.
echo Wait 10-15 seconds for everything to initialize, then:
echo  1. Open http://localhost:3000 in your browser
echo  2. Click "Begin Adventure"
echo  3. Start your epic quest!
echo.
echo Press any key to open browser...
pause >nul

start http://localhost:3000

echo.
echo To stop all services, close the terminal windows.
echo.
pause
