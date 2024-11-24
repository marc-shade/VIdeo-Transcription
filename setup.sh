#!/bin/bash

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "Conda is not installed. Please install Conda first."
    echo "Visit: https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

# Check if ffmpeg is installed
if ! command -v ffmpeg &> /dev/null; then
    echo "FFmpeg is not installed. Attempting to install..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if ! command -v brew &> /dev/null; then
            echo "Homebrew is not installed. Please install Homebrew first."
            echo "Visit: https://brew.sh"
            exit 1
        fi
        brew install ffmpeg
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        if command -v apt-get &> /dev/null; then
            sudo apt-get update && sudo apt-get install -y ffmpeg
        elif command -v yum &> /dev/null; then
            sudo yum install -y ffmpeg
        else
            echo "Could not install FFmpeg. Please install it manually."
            exit 1
        fi
    else
        echo "Unsupported operating system. Please install FFmpeg manually."
        exit 1
    fi
fi

# Create conda environment
echo "Creating conda environment 'video_env' with Python 3.11..."
conda create -n video_env python=3.11 -y

# Activate environment
echo "Activating conda environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate video_env

# Install dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Setup completed successfully!"
echo "To start using the application:"
echo "1. Run: conda activate video_env"
echo "2. Run: streamlit run main.py"
