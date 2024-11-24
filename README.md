# Video Transcription Agent 

A powerful video transcription and translation tool built using OpenAI's Whisper model, Google Translate, and a Streamlit-based interface. This project supports efficient client management, transcription of video files, and multi-language translation, providing users with a seamless workflow for converting video content to text.

![Screenshot 2024-11-01 at 12 24 40 PM (4)](https://github.com/user-attachments/assets/64923f59-8ade-4089-b910-8558eabfff35)

## Table of Contents
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [File Structure](#file-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Client Management**: Add, edit, view, and delete client profiles with a straightforward CRM interface.
- **Video Transcription**: Transcribe audio from video files using OpenAI's Whisper model, with optional timestamp inclusion.
- **Language Translation**: Translate transcriptions to multiple languages with Google Translate integration.
- **Bulk Import**: Process single video files or entire directories of videos.
- **Export Options**: Download selected or bulk transcription results in a text format.

## Installation

### Prerequisites

- **Python 3.11** (specifically tested with Python 3.11.10)
- **Conda** (recommended) or **virtualenv**
- **FFmpeg** (required for video processing)

### Quick Setup

We provide setup scripts for both Unix-based systems (macOS/Linux) and Windows:

#### Unix-based Systems (macOS/Linux)
```bash
# Make the setup script executable
chmod +x setup.sh

# Run the setup script
./setup.sh
```

#### Windows
```batch
# Run the setup script
setup.bat
```

These scripts will:
1. Check for required system dependencies (Conda, FFmpeg)
2. Create a new Conda environment with Python 3.11
3. Install all required Python packages
4. Guide you through starting the application

### Manual Setup

If you prefer to set up manually or the setup scripts don't work for your system, follow these steps:

### Installation Steps

1. **Install FFmpeg** (if not already installed):
   ```bash
   # On macOS using Homebrew
   brew install ffmpeg

   # On Ubuntu/Debian
   sudo apt-get update && sudo apt-get install ffmpeg

   # On Windows using Chocolatey
   choco install ffmpeg
   ```

2. **Create and activate a Conda environment**:
   ```bash
   # Create new environment with Python 3.11
   conda create -n video_env python=3.11
   
   # Activate the environment
   conda activate video_env
   ```

3. **Install dependencies**:
   ```bash
   # Install required packages
   pip install -r requirements.txt
   ```

### Troubleshooting Common Issues

1. **ModuleNotFoundError: No module named 'moviepy.editor'**
   - Try reinstalling moviepy with a specific version:
     ```bash
     pip install moviepy==1.0.3
     ```

2. **FFmpeg related errors**
   - Ensure FFmpeg is installed and accessible in your system PATH
   - For conda users, you can also install ffmpeg via conda:
     ```bash
     conda install ffmpeg
     ```

3. **Python version conflicts**
   - Make sure you're using Python 3.11
   - Check your Python version with:
     ```bash
     python --version
     ```

4. **Streamlit interface issues**
   - Install the watchdog module for better performance:
     ```bash
     pip install watchdog
     ```

## Usage

To start the application, run:

```bash
streamlit run main.py
```

This command will open a new browser window with the application interface. Follow the instructions below to interact with the app.

### Basic Workflow

1. **Client Management**:
   - Navigate to **Client Management** from the sidebar.
   - Add new clients or edit existing client profiles.
   - View, manage, and delete client transcriptions as needed.

2. **Transcription Service**:
   - Select an existing client from the dropdown or add a new client if none exist.
   - Upload a video file for transcription (supported formats: `.mp4`, `.avi`, `.mov`, `.mkv`, `.wmv`).
   - Choose optional settings such as timestamp inclusion and translation language.
   - Start the transcription process and view progress.
   - Download the generated transcription as a `.txt` file.

3. **Bulk Directory Import**:
   - For batch processing, input the path to a directory containing multiple video files.
   - Process the entire directory in one go, with individual progress tracking for each file.

## File Structure

```
VideoTranscription/
├── main.py                  # Main application entry point with Streamlit interface
├── crm.py                   # Client management interface and functionality
├── database.py              # SQLite database interaction logic
├── utils.py                 # Utility functions for video/audio handling, translation, and transcription
├── requirements.txt         # Dependencies
└── assets/                  # Additional resources (images, etc.)
```

### Main Files

- **`main.py`**: Hosts the Streamlit interface, manages navigation, and provides the video transcription process.
- **`crm.py`**: Contains the client relationship management system to add, view, edit, and delete clients and their transcriptions.
- **`database.py`**: Manages database connections and CRUD operations for clients and transcriptions.
- **`utils.py`**: Provides utilities for extracting audio, translating text, and transcribing audio using Whisper.

## Acknowledgments

This project was made possible with the following technologies:
- [OpenAI Whisper](https://github.com/openai/whisper)
- [Streamlit](https://streamlit.io/)
- [Google Translate API](https://py-googletrans.readthedocs.io/)
- [moviepy](https://zulko.github.io/moviepy/)
