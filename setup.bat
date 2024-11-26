@echo off
echo 🚀 Setting up Video Transcription with AI Persona...

REM Check Python version
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is required but not found. Please install Python 3.11 or higher.
    exit /b 1
)

REM Check FFmpeg
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FFmpeg is required but not found.
    echo Please install FFmpeg from https://ffmpeg.org/download.html
    exit /b 1
)

REM Check Ollama
ollama -v >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ollama is required but not found.
    echo Please install Ollama from https://ollama.ai
    exit /b 1
)

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

echo ✨ Setup complete! To start the application:
echo 1. Start Ollama server: ollama serve
echo 2. Pull a model (if not done): ollama pull mistral:instruct
echo 3. Run the app: streamlit run main.py
