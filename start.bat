@echo off
echo.
echo  FamilyForge - starting...
echo.

REM Create virtual environment if it does not exist
if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

call .venv\Scripts\activate.bat

echo Installing / updating packages (first run may take a minute)...
pip install -r requirements.txt --quiet

echo.
echo Launching FamilyForge...
echo A browser window should open shortly.
echo.
streamlit run app.py

pause
