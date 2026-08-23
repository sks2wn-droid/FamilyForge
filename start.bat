@echo off
setlocal EnableDelayedExpansion
title FamilyForge Launcher
color 0A

echo.
echo  ================================================
echo       FamilyForge - Family Photo Helper
echo  ================================================
echo.

cd /d "%~dp0"
echo Working folder: %CD%
echo.

REM ---------- Check for Python ----------
set PYTHON_CMD=
python --version >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python
    echo Found Python via "python"
) else (
    py -3 --version >nul 2>&1
    if !errorlevel!==0 (
        set PYTHON_CMD=py -3
        echo Found Python via "py -3"
    )
)

if "%PYTHON_CMD%"=="" (
    echo.
    echo  ERROR: Python was not found.
    echo.
    echo  Please install Python 3.10 or newer from:
    echo  https://www.python.org/downloads/
    echo.
    echo  IMPORTANT: During install, CHECK the box
    echo  "Add python.exe to PATH"
    echo.
    echo  Then close this window and run start.bat again.
    echo.
    pause
    exit /b 1
)

echo Using: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM ---------- Create venv if needed ----------
if not exist ".venv" (
    echo Creating private environment (first time only)...
    %PYTHON_CMD% -m venv .venv
    if errorlevel 1 (
        echo.
        echo  ERROR: Could not create virtual environment.
        echo  Try running this Command Prompt as Administrator
        echo  or check that Python is installed correctly.
        echo.
        pause
        exit /b 1
    )
    echo Environment created.
) else (
    echo Private environment already exists.
)

echo.
echo Activating environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate the environment.
    pause
    exit /b 1
)

echo.
echo Installing / updating packages...
echo (This can take 1-3 minutes the first time - please wait)
echo.
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo  ERROR: Package installation failed.
    echo  Check your internet connection and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo  Packages ready.
echo.
echo  Starting FamilyForge...
echo  A browser window should open automatically.
echo  If it does not, look for a line that says
echo  "Local URL: http://localhost:8501" and open that.
echo.
echo  Keep THIS window open while you use the app.
echo  Close it when you are finished.
echo.
echo  ================================================
echo.

streamlit run app.py --server.headless false

echo.
echo FamilyForge has stopped.
pause
