import whisper
from moviepy.editor import VideoFileClip
import tempfile
import os
from deep_translator import GoogleTranslator
import soundfile as sf
import librosa

def is_valid_video_format(filename):
    """
    Check if the video format is supported
    """
    valid_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.m4a']
    return os.path.splitext(filename.lower())[1] in valid_extensions

def extract_audio(video_path):
    """
    Extract audio from video or audio file
    """
    try:
        # Determine file type
        file_extension = os.path.splitext(video_path)[1].lower()
        
        # Create temporary file for audio
        temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        temp_audio_path = temp_audio.name
        temp_audio.close()

        # If it's already an audio file, just convert it
        if file_extension in ['.m4a', '.mp3', '.wav', '.flac', '.ogg']:
            # Read the audio file
            audio, sample_rate = librosa.load(video_path, sr=None)
            
            # Write to wav
            sf.write(temp_audio_path, audio, sample_rate)
            
            return temp_audio_path

        # If it's a video file, use moviepy
        video = VideoFileClip(video_path)
        
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
        translator = GoogleTranslator(source='auto', target=target_language.lower())
        
        if '[' in text and ']' in text:  # Text contains timestamps
            # Split the text into segments and translate each segment separately
            segments = text.split('\n')
            translated_segments = []
            
            for segment in segments:
                if segment.strip():  # Skip empty lines
                    # Extract timestamp if present
                    timestamp = ''
                    content = segment
                    if segment.startswith('[') and ']' in segment:
                        timestamp = segment[:segment.index(']') + 1]
                        content = segment[segment.index(']') + 1:].strip()
                    
                    # Translate content if it's not empty
                    if content:
                        translated_content = translator.translate(content)
                        translated_segments.append(f"{timestamp} {translated_content}" if timestamp else translated_content)
                    else:
                        translated_segments.append(segment)
                else:
                    translated_segments.append(segment)
            
            return '\n'.join(translated_segments)
        else:
            # Translate the entire text at once if no timestamps
            return translator.translate(text)
    except Exception as e:
        raise Exception(f"Error translating text: {str(e)}")

def get_available_languages():
    """
    Returns a dictionary of available languages for translation
    """
    return {
        'af': 'Afrikaans', 'sq': 'Albanian', 'am': 'Amharic', 'ar': 'Arabic',
        'hy': 'Armenian', 'az': 'Azerbaijani', 'eu': 'Basque', 'be': 'Belarusian',
        'bn': 'Bengali', 'bs': 'Bosnian', 'bg': 'Bulgarian', 'ca': 'Catalan',
        'ceb': 'Cebuano', 'zh-CN': 'Chinese (Simplified)', 'zh-TW': 'Chinese (Traditional)',
        'co': 'Corsican', 'hr': 'Croatian', 'cs': 'Czech', 'da': 'Danish',
        'nl': 'Dutch', 'en': 'English', 'eo': 'Esperanto', 'et': 'Estonian',
        'fi': 'Finnish', 'fr': 'French', 'fy': 'Frisian', 'gl': 'Galician',
        'ka': 'Georgian', 'de': 'German', 'el': 'Greek', 'gu': 'Gujarati',
        'ht': 'Haitian Creole', 'ha': 'Hausa', 'haw': 'Hawaiian', 'he': 'Hebrew',
        'hi': 'Hindi', 'hmn': 'Hmong', 'hu': 'Hungarian', 'is': 'Icelandic',
        'ig': 'Igbo', 'id': 'Indonesian', 'ga': 'Irish', 'it': 'Italian',
        'ja': 'Japanese', 'jv': 'Javanese', 'kn': 'Kannada', 'kk': 'Kazakh',
        'km': 'Khmer', 'rw': 'Kinyarwanda', 'ko': 'Korean', 'ku': 'Kurdish',
        'ky': 'Kyrgyz', 'lo': 'Lao', 'la': 'Latin', 'lv': 'Latvian',
        'lt': 'Lithuanian', 'lb': 'Luxembourgish', 'mk': 'Macedonian',
        'mg': 'Malagasy', 'ms': 'Malay', 'ml': 'Malayalam', 'mt': 'Maltese',
        'mi': 'Maori', 'mr': 'Marathi', 'mn': 'Mongolian', 'my': 'Myanmar',
        'ne': 'Nepali', 'no': 'Norwegian', 'ny': 'Nyanja', 'or': 'Odia',
        'ps': 'Pashto', 'fa': 'Persian', 'pl': 'Polish', 'pt': 'Portuguese',
        'pa': 'Punjabi', 'ro': 'Romanian', 'ru': 'Russian', 'sm': 'Samoan',
        'gd': 'Scots Gaelic', 'sr': 'Serbian', 'st': 'Sesotho', 'sn': 'Shona',
        'sd': 'Sindhi', 'si': 'Sinhala', 'sk': 'Slovak', 'sl': 'Slovenian',
        'so': 'Somali', 'es': 'Spanish', 'su': 'Sundanese', 'sw': 'Swahili',
        'sv': 'Swedish', 'tl': 'Tagalog', 'tg': 'Tajik', 'ta': 'Tamil',
        'tt': 'Tatar', 'te': 'Telugu', 'th': 'Thai', 'tr': 'Turkish',
        'tk': 'Turkmen', 'uk': 'Ukrainian', 'ur': 'Urdu', 'ug': 'Uyghur',
        'uz': 'Uzbek', 'vi': 'Vietnamese', 'cy': 'Welsh', 'xh': 'Xhosa',
        'yi': 'Yiddish', 'yo': 'Yoruba', 'zu': 'Zulu'
    }

def transcribe_audio(audio_path, include_timestamps=True):
    """
    Transcribe audio file using Whisper with optional timestamps
    """
    try:
        # Load model
        model = whisper.load_model("base")
        
        # Transcribe
        result = model.transcribe(audio_path)
        
        if include_timestamps:
            # Format with timestamps
            formatted_segments = []
            for segment in result["segments"]:
                timestamp = format_timestamp(segment["start"])
                text = segment["text"].strip()
                formatted_segments.append(f"[{timestamp}] {text}")
            return "\n".join(formatted_segments)
        else:
            # Return plain text
            return result["text"]
    except Exception as e:
        raise Exception(f"Error transcribing audio: {str(e)}")
