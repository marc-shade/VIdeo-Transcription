import whisper
from moviepy.editor import VideoFileClip
import tempfile
import os
from googletrans import Translator

def is_valid_video_format(filename):
    """
    Check if the video format is supported
    """
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv']
    return os.path.splitext(filename.lower())[1] in valid_extensions

def extract_audio(video_path):
    """
    Extract audio from video file
    """
    try:
        # Load video
        video = VideoFileClip(video_path)
        
        # Create temporary file for audio
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_path = temp_audio.name
        temp_audio.close()

        # Extract audio
        video.audio.write_audiofile(temp_audio_path, verbose=False, logger=None)
        video.close()

        return temp_audio_path
    except Exception as e:
        raise Exception(f"Error extracting audio: {str(e)}")

def format_timestamp(seconds):
    """
    Format seconds into HH:MM:SS
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def translate_text(text, target_language):
    """
    Translate text to target language
    """
    try:
        translator = Translator()
        if '[' in text and ']' in text:  # Text contains timestamps
            # Split the text into segments and translate each segment separately
            segments = text.split('\n')
            translated_segments = []
            for segment in segments:
                # Separate timestamp and text
                timestamp = segment[:segment.find(']') + 1]
                content = segment[segment.find(']') + 1:]
                # Translate only the content
                translated_content = translator.translate(content.strip(), dest=target_language).text
                translated_segments.append(f"{timestamp} {translated_content}")
            return '\n'.join(translated_segments)
        else:
            return translator.translate(text, dest=target_language).text
    except Exception as e:
        raise Exception(f"Error translating text: {str(e)}")

def get_available_languages():
    """
    Returns a dictionary of available languages for translation
    """
    return {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh-cn': 'Chinese (Simplified)',
        'ar': 'Arabic',
        'hi': 'Hindi'
    }

def transcribe_audio(audio_path, include_timestamps=True):
    """
    Transcribe audio file using Whisper with optional timestamps
    """
    try:
        # Load Whisper model (using "base" for balance of speed and accuracy)
        model = whisper.load_model("base")
        
        # Transcribe audio with word-level timestamps if requested
        result = model.transcribe(audio_path, word_timestamps=include_timestamps)
        
        if include_timestamps:
            # Format the transcription with timestamps for each segment
            formatted_transcription = []
            for segment in result["segments"]:
                start_time = format_timestamp(segment["start"])
                end_time = format_timestamp(segment["end"])
                text = segment["text"].strip()
                formatted_transcription.append(f"[{start_time} - {end_time}] {text}")
            return "\n".join(formatted_transcription)
        else:
            # Return plain text without timestamps
            return result["text"]
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")
