#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "🚀 Setting up Video Transcription with AI Persona..."

# Check Python version
if command_exists python3; then
    python_version=$(python3 --version 2>&1 | awk '{print $2}')
    echo "✓ Found Python version $python_version"
else
    echo "❌ Python 3 is required but not found. Please install Python 3.11 or higher."
    exit 1
fi

# Check if FFmpeg is installed
if command_exists ffmpeg; then
    echo "✓ FFmpeg is installed"
else
    echo "❌ FFmpeg is required but not found."
    echo "Please install FFmpeg:"
    echo "- macOS: brew install ffmpeg"
    echo "- Linux: sudo apt-get install ffmpeg"
    echo "- Windows: Download from https://ffmpeg.org/download.html"
    exit 1
fi

# Check if Ollama is installed
if command_exists ollama; then
    echo "✓ Ollama is installed"
else
    echo "❌ Ollama is required but not found."
    echo "Please install Ollama from https://ollama.ai"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

echo "✨ Setup complete! To start the application:"
echo "1. Start Ollama server: ollama serve"
echo "2. Pull a model (if not done): ollama pull mistral:instruct"
echo "3. Run the app: streamlit run main.py"
