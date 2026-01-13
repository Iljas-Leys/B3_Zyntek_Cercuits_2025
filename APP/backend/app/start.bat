@echo off
echo ============================================
echo Agent TSE Backend - Quick Start
echo ============================================
echo.

::REM Check if virtual environment exists
::IF NOT EXIST .venv (
::    echo Creating virtual environment...
::    python -m venv .venv
::    echo.
::)

::REM Activate virtual environment
::echo Activating virtual environment...
::CALL .venv\Scripts\activate
::echo.

::REM Install/update requirements
::echo Installing/updating dependencies...
::python -m pip install --upgrade pip
::pip install -r requirements.txt
::echo.

REM Ask if user wants to initialize database
echo.
set /p INIT_DB="Initialize database with test data? (y/n): "
if /i "%INIT_DB%"=="y" (
    echo.
    echo Running database initialization...
    python init_db.py
    echo.
)

REM Start the server
echo ============================================
echo Starting FastAPI server...
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo ============================================
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn app.main:app --reload

pause