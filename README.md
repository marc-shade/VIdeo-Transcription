# Video Transcription Agent 🎥

A powerful video transcription and translation tool built using OpenAI's Whisper model, Google Translate, and a Streamlit-based interface. This project supports efficient client management, transcription of video files, and multi-language translation, providing users with a seamless workflow for converting video content to text.

![Video Transcription Agent Screenshot](assets/demo_screenshot.png) <!-- Optional: Add a screenshot of the app -->

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

- **Python 3.7+**
- **Virtual Environment** (recommended): Set up a virtual environment to manage dependencies.

### Clone the Repository

```bash
git clone https://github.com/marc-shade/Video-Transcription.git
cd Video-Transcription
```

### Install Dependencies

Use the following command to install the required dependencies:

```bash
pip install -r requirements.txt
```

The requirements include:
- `streamlit`: For the web interface.
- `whisper`: For transcription using OpenAI’s Whisper model.
- `moviepy`: To handle video and audio extraction.
- `googletrans`: For translating transcriptions to multiple languages.
- `sqlite3`: For database management.

### Database Initialization

The application will create a SQLite database (`transcription.db`) if it does not exist. This database will store client information and transcription data.

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
