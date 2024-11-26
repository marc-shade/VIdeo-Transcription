import streamlit as st
import tempfile
import os
import requests
from utils import (
    extract_audio, transcribe_audio, is_valid_video_format,
    translate_text, get_available_languages
)
from database import TranscriptionDB
import ai_persona
from typing import Tuple, Optional
import json

def initialize_session_state():
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'ollama_settings' not in st.session_state:
        st.session_state.ollama_settings = {
            'api_base': "http://localhost:11434",
            'model': "mistral:instruct",
            'temperature': 0.7,
            'top_p': 0.9,
            'top_k': 40,
            'repeat_penalty': 1.1,
            'max_tokens': 1024,
            'context_window': 4096
        }
    if 'show_settings' not in st.session_state:
        st.session_state.show_settings = False

def save_settings():
    """Save current settings to a JSON file."""
    settings_file = "settings.json"
    try:
        with open(settings_file, 'w') as f:
            json.dump(st.session_state.ollama_settings, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving settings: {str(e)}")
        return False

def load_settings():
    """Load settings from JSON file."""
    settings_file = "settings.json"
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
            st.session_state.ollama_settings.update(settings)
        return True
    except FileNotFoundError:
        return False
    except Exception as e:
        print(f"Error loading settings: {str(e)}")
        return False

def render_sidebar_settings():
    """Render Ollama settings in the sidebar."""
    st.sidebar.title("🎥 Video Transcription")
    
    # Ollama API settings in a collapsible section
    with st.sidebar.expander("🤖 AI Settings", expanded=False):
        st.subheader("Ollama Configuration")
        
        # API Base URL
        api_base = st.text_input(
            "API Base URL",
            value=st.session_state.ollama_settings['api_base'],
            help="The base URL for your Ollama instance"
        )
        
        # Fetch available models
        try:
            available_models = ai_persona.PersonaAnalyzer.get_available_models(api_base)
        except:
            available_models = ["mistral:instruct"]
            st.error("⚠️ Could not fetch models. Is Ollama running?")
        
        # Model selection
        model = st.selectbox(
            "Model",
            options=available_models,
            index=available_models.index(st.session_state.ollama_settings['model']) if st.session_state.ollama_settings['model'] in available_models else 0,
            help="Select the AI model to use for persona generation and chat"
        )
        
        # Advanced model parameters
        st.subheader("Model Parameters")
        
        col1, col2 = st.columns(2)
        with col1:
            temperature = st.slider(
                "Temperature",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state.ollama_settings['temperature'],
                step=0.1,
                help="Controls randomness in responses"
            )
            
            top_p = st.slider(
                "Top P",
                min_value=0.0,
                max_value=1.0,
                value=st.session_state.ollama_settings['top_p'],
                step=0.1,
                help="Nucleus sampling threshold"
            )
            
            repeat_penalty = st.slider(
                "Repeat Penalty",
                min_value=1.0,
                max_value=2.0,
                value=st.session_state.ollama_settings['repeat_penalty'],
                step=0.1,
                help="Penalty for repeating tokens"
            )
        
        with col2:
            top_k = st.slider(
                "Top K",
                min_value=1,
                max_value=100,
                value=st.session_state.ollama_settings['top_k'],
                help="Limits vocabulary in responses"
            )
            
            max_tokens = st.slider(
                "Max Tokens",
                min_value=128,
                max_value=4096,
                value=st.session_state.ollama_settings['max_tokens'],
                step=128,
                help="Maximum response length"
            )
            
            context_window = st.slider(
                "Context Window",
                min_value=512,
                max_value=8192,
                value=st.session_state.ollama_settings['context_window'],
                step=512,
                help="Token context window size"
            )
        
        # Save settings button
        col1, col2 = st.columns(2)
        with col1:
            if st.button("💾 Save Settings"):
                if save_settings():
                    st.success("Settings saved!")
                else:
                    st.error("Failed to save settings")
        
        with col2:
            if st.button("🔄 Reset Defaults"):
                st.session_state.ollama_settings = {
                    'api_base': "http://localhost:11434",
                    'model': "mistral:instruct",
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'top_k': 40,
                    'repeat_penalty': 1.1,
                    'max_tokens': 1024,
                    'context_window': 4096
                }
                st.experimental_rerun()
        
        # Update settings if changed
        current_settings = {
            'api_base': api_base,
            'model': model,
            'temperature': temperature,
            'top_p': top_p,
            'top_k': top_k,
            'repeat_penalty': repeat_penalty,
            'max_tokens': max_tokens,
            'context_window': context_window
        }
        
        if current_settings != st.session_state.ollama_settings:
            st.session_state.ollama_settings.update(current_settings)
            st.rerun()
    
    # Client Management section
    with st.sidebar.expander("👥 Client Management", expanded=False):
        st.subheader("Add New Client")
        with st.form("add_client_form"):
            new_name = st.text_input("Client Name")
            new_email = st.text_input("Client Email")
            
            if st.form_submit_button("Add Client"):
                if new_name and new_email:
                    try:
                        db.add_client(new_name, new_email)
                        st.success("Client added successfully!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error adding client: {str(e)}")
                else:
                    st.error("Please fill in all fields!")

def get_persona_analyzer() -> ai_persona.PersonaAnalyzer:
    """Get a PersonaAnalyzer instance with current settings."""
    options = {
        "temperature": st.session_state.ollama_settings['temperature'],
        "top_p": st.session_state.ollama_settings['top_p'],
        "top_k": st.session_state.ollama_settings['top_k'],
        "repeat_penalty": st.session_state.ollama_settings['repeat_penalty'],
        "num_predict": st.session_state.ollama_settings['max_tokens'],
        "num_ctx": st.session_state.ollama_settings['context_window']
    }
    return ai_persona.PersonaAnalyzer(
        model=st.session_state.ollama_settings['model'],
        api_base=st.session_state.ollama_settings['api_base'],
        options=options
    )

def get_client_list():
    """Get list of clients for dropdown."""
    db = TranscriptionDB()
    clients = db.get_all_clients()
    return {f"{client[1]} ({client[2]})": client[0] for client in clients}

def check_environment():
    """Check if all required environment variables are set."""
    try:
        # Check if Ollama is running by making a test request
        response = requests.get("http://localhost:11434/api/version")
        if response.status_code != 200:
            st.error("❌ Ollama server is not running. Please start Ollama first.")
            st.stop()
        st.success("✅ Ollama server is running")
        return True
    except requests.exceptions.ConnectionError:
        st.error("❌ Ollama server is not running. Please start Ollama first.")
        st.stop()
    return False

def regenerate_persona_for_transcription(transcription_id: int, original_text: str, db: TranscriptionDB) -> Tuple[bool, Optional[str]]:
    """Regenerate persona prompt for an existing transcription."""
    analyzer = get_persona_analyzer()
    try:
        persona_name, system_prompt = analyzer.analyze_transcript(original_text)
        
        if persona_name and system_prompt and len(system_prompt.strip()) > 0:
            success = db.update_persona_prompt(transcription_id, persona_name, system_prompt)
            if success:
                return True, persona_name
        return False, None
    except Exception as e:
        print(f"Error regenerating persona: {str(e)}")
        return False, None

def render_persona_chat(db: TranscriptionDB, transcription_id: int, original_text: str):
    """Render the persona chat interface."""
    # Initialize session state for messages if not exists
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Get persona data
    persona_data = db.get_persona_prompt(transcription_id)
    if not persona_data:
        return

    persona_name, system_prompt = persona_data
    
    # Display the system prompt in a container with toggle
    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"**Persona Name:** {persona_name}")
    with col2:
        if st.button("🔄 Regenerate", key=f"regen_{transcription_id}"):
            with st.spinner("Regenerating persona..."):
                success, new_name = regenerate_persona_for_transcription(transcription_id, original_text, db)
                if success:
                    st.success(f"Regenerated persona as '{new_name}'!")
                    st.rerun()
                else:
                    st.error("Failed to regenerate persona. Please try again.")
    
    if "show_prompt" not in st.session_state:
        st.session_state.show_prompt = False
    
    if st.button("Toggle Persona Details", key=f"toggle_{transcription_id}"):
        st.session_state.show_prompt = not st.session_state.show_prompt
    
    if st.session_state.show_prompt:
        st.markdown("**System Prompt:**")
        st.text_area("", system_prompt, height=100, disabled=True, key=f"prompt_{transcription_id}")
        st.markdown("---")

    # Chat interface
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Ask a question..."):
        with st.chat_message("user"):
            st.markdown(prompt)
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("assistant"):
            analyzer = get_persona_analyzer()
            response = analyzer.generate_response(system_prompt, prompt)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})

def generate_persona_for_transcription(transcription_id: int, original_text: str, db: TranscriptionDB):
    """Generate a persona prompt for an existing transcription."""
    analyzer = get_persona_analyzer()
    try:
        persona_name, system_prompt = analyzer.analyze_transcript(original_text)
        
        if persona_name and system_prompt and len(system_prompt.strip()) > 0:
            db.add_persona_prompt(transcription_id, persona_name, system_prompt)
            return True, persona_name
        else:
            print("Error: Empty persona or system prompt generated")
            return False, None
    except Exception as e:
        print(f"Error generating persona: {str(e)}")
        return False, None

def process_video(video_path, client_id, include_timestamps, target_language, languages, db, progress_container, progress_bar, status_text, filename):
    """Process a single video file."""
    try:
        # Stage 1: Audio extraction (20% of progress)
        status_text.text("Extracting audio from video...")
        audio_path = extract_audio(video_path)
        progress_bar.progress(0.2)

        # Stage 2: Transcription (40% of progress)
        status_text.text("Transcribing audio...")
        transcription = transcribe_audio(audio_path, include_timestamps)
        progress_bar.progress(0.4)

        # Stage 3: Translation if needed (60% of progress)
        translated_text = None
        if target_language and target_language != "None":
            status_text.text(f"Translating to {languages[target_language]}...")
            translated_text = translate_text(transcription, target_language)
        progress_bar.progress(0.6)

        # Stage 4: Save to database (80% of progress)
        status_text.text("Saving transcription...")
        transcription_id = db.add_transcription(
            client_id, filename, transcription,
            translated_text, target_language
        )
        progress_bar.progress(0.8)

        # Stage 5: Generate AI Persona (100% of progress)
        status_text.text("Generating AI persona...")
        analyzer = get_persona_analyzer()
        persona_result = analyzer.analyze_transcript(transcription)
        db.add_persona_prompt(
            transcription_id,
            persona_result["persona_name"],
            persona_result["persona_prompt"]
        )
        progress_bar.progress(1.0)

        # Cleanup
        if os.path.exists(audio_path):
            os.unlink(audio_path)

        return transcription, translated_text, transcription_id

    except Exception as e:
        st.error(f"Error processing video: {str(e)}")
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.unlink(audio_path)
        return None, None, None

def render_transcription_interface():
    """Main interface for the transcription app."""
    check_environment()
    initialize_session_state()
    load_settings()  # Load saved settings if available
    render_sidebar_settings()
    st.title("🎥 Video to Text Transcription")
    
    # Initialize database
    db = TranscriptionDB()
    
    # Sidebar for client selection/creation
    with st.sidebar:
        st.subheader("👤 Client Management")
        tab1, tab2 = st.tabs(["Select Client", "New Client"])
        
        with tab1:
            clients = get_client_list()
            selected_client = st.selectbox(
                "Select a client",
                options=list(clients.keys()) if clients else [],
                format_func=lambda x: x,
                key="client_select"
            )
            client_id = clients[selected_client] if selected_client else None
        
        with tab2:
            with st.form("new_client_form"):
                new_name = st.text_input("Name")
                new_email = st.text_input("Email")
                if st.form_submit_button("Add Client"):
                    if new_name and new_email:
                        try:
                            db.add_client(new_name, new_email)
                            st.success("Client added successfully!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error adding client: {str(e)}")
                    else:
                        st.error("Please fill in all fields!")

    # Main content area
    tab1, tab2 = st.tabs(["🎥 Upload & Transcribe", "📚 View Transcriptions"])
    
    with tab1:
        st.markdown("""
        Upload your video file to get the transcribed text and AI persona analysis.
        Supported formats: MP4, AVI, MOV, MKV, WMV
        """)

        if not client_id:
            st.warning("Please select or create a client first!")
            return

        uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov', 'mkv', 'wmv'])
        
        col1, col2 = st.columns(2)
        with col1:
            include_timestamps = st.checkbox("Include timestamps", value=True)
        with col2:
            languages = get_available_languages()
            target_language = st.selectbox(
                "Translate to",
                options=["None"] + list(languages.keys()),
                format_func=lambda x: "Original" if x == "None" else languages[x]
            )

        if uploaded_file:
            if not is_valid_video_format(uploaded_file.name):
                st.error("Please upload a valid video file!")
                return

            with st.spinner("Processing video..."):
                # Create progress tracking components
                progress_container = st.empty()
                progress_bar = progress_container.progress(0)
                status_text = st.empty()

                # Save uploaded file temporarily
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
                    tmp_file.write(uploaded_file.read())
                    video_path = tmp_file.name

                try:
                    # Process the video
                    transcription, translation, transcription_id = process_video(
                        video_path, client_id, include_timestamps,
                        target_language if target_language != "None" else None,
                        languages, db, progress_container, progress_bar,
                        status_text, uploaded_file.name
                    )

                    if transcription and transcription_id:
                        st.success("Video processed successfully!")
                        
                        # Display results in tabs
                        result_tabs = st.tabs(["📝 Transcription", "🔄 Translation", "🤖 AI Persona"] if translation else ["📝 Transcription", "🤖 AI Persona"])
                        
                        with result_tabs[0]:
                            st.text_area("Original Text", transcription, height=300)
                            
                        if translation:
                            with result_tabs[1]:
                                st.text_area(f"Translation ({languages[target_language]})", translation, height=300)
                        
                        with result_tabs[-1]:
                            render_persona_chat(db, transcription_id, transcription)

                finally:
                    # Cleanup
                    if os.path.exists(video_path):
                        os.unlink(video_path)

    with tab2:
        if not client_id:
            st.warning("Please select a client to view their transcriptions!")
            return

        transcriptions = db.get_client_transcriptions(client_id)
        if not transcriptions:
            st.info("No transcriptions found for this client.")
            return

        for t in transcriptions:
            with st.expander(f"📝 {t[2]} - {t[6]}"):
                st.text_area("Original Text", t[3], height=150)
                if t[4]:  # If there's a translation
                    language_display = languages.get(t[5], "Unknown")
                    st.text_area(f"Translation ({language_display})", t[4], height=150)
                
                # Add persona management section
                st.markdown("---")
                st.subheader("AI Persona")
                
                # Get existing persona data
                persona_data = db.get_persona_prompt(t[0])
                
                if persona_data:
                    render_persona_chat(db, t[0], t[3])
                else:
                    st.warning("No persona available for this transcription")
                    if st.button("Generate Persona", key=f"gen_{t[0]}"):
                        with st.spinner("Generating persona..."):
                            success, persona_name = generate_persona_for_transcription(t[0], t[3], db)
                            if success:
                                st.success(f"Generated persona '{persona_name}'!")
                                st.rerun()
                            else:
                                st.error("Failed to generate persona. Please try again.")

if __name__ == "__main__":
    render_transcription_interface()
