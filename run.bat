@echo off
REM Smart Document Field & Value Extractor - Windows Run Script

echo 🚀 Starting Smart Document Field & Value Extractor...

REM Check if virtual environment exists
if not exist ".venv" (
    echo ❌ Virtual environment not found. Please run setup.bat first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo 🔄 Activating virtual environment...
call .venv\Scripts\activate

REM Check if streamlit is installed
streamlit --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Streamlit not found. Please run setup.bat first.
    pause
    exit /b 1
)

echo ✅ Starting Streamlit application...
echo 🌐 The app will open in your browser at http://localhost:8501
echo.

REM Run the application
streamlit run app.py
