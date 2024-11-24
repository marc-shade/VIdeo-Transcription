@echo off
SETLOCAL

:: Check if conda is installed
where conda >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Conda is not installed. Please install Conda first.
    echo Visit: https://docs.conda.io/en/latest/miniconda.html
    exit /b 1
)

:: Check if ffmpeg is installed
where ffmpeg >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo FFmpeg is not installed. Please install it using one of these methods:
    echo 1. Install using Chocolatey: choco install ffmpeg
    echo 2. Download from: https://www.gyan.dev/ffmpeg/builds/
    echo Add FFmpeg to your system PATH and run this script again.
    exit /b 1
)

:: Create conda environment
echo Creating conda environment 'video_env' with Python 3.11...
call conda create -n video_env python=3.11 -y
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create conda environment.
    exit /b 1
)

:: Activate environment
echo Activating conda environment...
call conda activate video_env
if %ERRORLEVEL% NEQ 0 (
    echo Failed to activate conda environment.
    exit /b 1
)

:: Install dependencies
echo Installing Python dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Failed to install dependencies.
    exit /b 1
)

echo Setup completed successfully!
echo To start using the application:
echo 1. Run: conda activate video_env
echo 2. Run: streamlit run main.py

ENDLOCAL
