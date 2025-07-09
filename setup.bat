@echo off
REM Smart Document Field & Value Extractor - Windows Setup Script

echo 🚀 Setting up Smart Document Field & Value Extractor...

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.7 or higher.
    pause
    exit /b 1
)

echo ✅ Python found

REM Create virtual environment if it doesn't exist
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
) else (
    echo ✅ Virtual environment already exists
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate

REM Install requirements
echo 📥 Installing dependencies...
pip install -r requirements.txt

echo ✅ Setup complete!
echo.
echo 🎉 To run the application:
echo    1. Activate the virtual environment: .venv\Scripts\activate
echo    2. Run the app: streamlit run app.py
echo.
echo 📖 Or simply run: run.bat
echo.
pause
