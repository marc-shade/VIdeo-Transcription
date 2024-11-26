# 🎥 AI Video Transcription with Persona Generation

A powerful video transcription tool that not only transcribes videos but also generates AI personas that can engage in conversations about the content. Built with Streamlit and powered by Ollama for local AI processing.

## ✨ Features

- 🎬 Video to text transcription using Whisper
- 🌐 Multi-language translation support
- 🤖 AI persona generation from transcripts
- 💬 Interactive chat with generated personas
- 🔄 Dynamic model selection from local Ollama installation
- 📊 Client and transcription management
- 🔒 Local AI processing with Ollama

## 🚀 Recent Updates

- Added dynamic Ollama model selection
- Improved persona generation and chat interface
- Added ability to regenerate personas
- Enhanced error handling and feedback
- Improved database management with migrations

## 🛠️ Prerequisites

1. Python 3.11 or higher
2. FFmpeg installed on your system
3. [Ollama](https://ollama.ai/) installed and running
4. At least one Ollama model pulled (e.g., `ollama pull mistral:instruct`)

## 📦 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Video-Transcription.git
cd Video-Transcription
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install FFmpeg (if not already installed):
- macOS: `brew install ffmpeg`
- Windows: Download from [FFmpeg website](https://ffmpeg.org/download.html)
- Linux: `sudo apt-get install ffmpeg`

5. Install and start Ollama:
- Follow instructions at [ollama.ai](https://ollama.ai/)
- Pull a model: `ollama pull mistral:instruct`

## 🚀 Usage

1. Start the Ollama server:
```bash
ollama serve
```

2. Run the application:
```bash
streamlit run main.py
```

3. Access the web interface at `http://localhost:8501`

## 💡 Features in Detail

### Video Transcription
- Upload video files
- Automatic transcription using Whisper
- Optional timestamp inclusion
- Support for multiple video formats

### Translation
- Translate transcriptions to multiple languages
- Powered by deep-translator
- Maintains formatting and structure

### AI Persona Generation
- Analyzes speaking patterns and content
- Creates context-aware personas
- Generates detailed system prompts
- Supports multiple Ollama models
- Regenerate personas as needed

### Interactive Chat
- Chat with generated personas
- Context-aware responses
- Maintains chat history
- Real-time response generation

## 🔧 Configuration

The application uses several environment variables that can be set in a `.env` file:

```env
OLLAMA_API_BASE=http://localhost:11434
DEFAULT_MODEL=mistral:instruct
```

## 📝 Database Schema

The application uses SQLite with the following main tables:
- clients: Store client information
- transcriptions: Store video transcriptions
- persona_prompts: Store generated AI personas

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- OpenAI Whisper for transcription
- Ollama for local AI processing
- Streamlit for the web interface
- All other open-source contributors
