import streamlit as st
import tempfile
import os
from utils import (
    extract_audio, transcribe_audio, is_valid_video_format,
    translate_text, get_available_languages
)
from crm import render_crm_interface, render_client_form
from database import TranscriptionDB
import time

# Page configuration
st.set_page_config(
    page_title="Video Transcription Agent",
    page_icon="🎥",
    layout="wide"
)

def get_client_choices():
    """Get list of clients for dropdown."""
    db = TranscriptionDB()
    clients = db.get_all_clients()
    return {f"{client[1]} ({client[2]})": client[0] for client in clients}

def process_video(video_path, client_id, include_timestamps, target_language, languages, db, progress_container, progress_bar, status_text, filename):
    """Process a single video file."""
    try:
        # Stage 1: Audio extraction (30% of progress)
        status_text.text("Extracting audio from video...")
        audio_path = extract_audio(video_path)
        progress_bar.progress(30)
        
        # Stage 2: Transcribe audio (takes the longest, 40% more progress)
        status_text.text("Transcribing audio... This might take a while.")
        transcription = transcribe_audio(audio_path, include_timestamps=include_timestamps)
        progress_bar.progress(70)
        
        # Stage 3: Translation if selected (20% of progress)
        if target_language:
            status_text.text(f"Translating to {languages[target_language]}...")
            transcription = translate_text(transcription, target_language)
        progress_bar.progress(90)

        # Save to database
        db.add_transcription(
            client_id=client_id,
            original_filename=filename,
            transcription_text=transcription,
            include_timestamps=include_timestamps,
            target_language=target_language if target_language else None
        )

        # Clean up temporary files
        os.unlink(audio_path)
        return transcription  # Return the transcription text
    except Exception as e:
        st.error(f"Error processing video {filename}: {str(e)}")
        if 'audio_path' in locals() and os.path.exists(audio_path):
            os.unlink(audio_path)
        return None

def render_transcription_interface():
    st.title("🎥 Video to Text Transcription")
    st.markdown("""
    Upload your video file to get the transcribed text using OpenAI's Whisper model.
    Supported formats: MP4, AVI, MOV, MKV, WMV
    """)

    # Initialize database
    db = TranscriptionDB()

    # Client selection section
    st.subheader("Select or Add Client")
    col1, col2 = st.columns([3, 1], gap="small", vertical_alignment="bottom")
    
    with col1:
        # Get client choices and create dropdown
        client_choices = get_client_choices()
        if client_choices:
            selected_client = st.selectbox(
                "Select Client",
                options=[""] + list(client_choices.keys()),
                format_func=lambda x: "Select a client..." if x == "" else x
            )
            client_id = client_choices.get(selected_client)
        else:
            st.info("No clients found. Please add a new client to continue.")
            selected_client = ""
            client_id = None

    with col2:
        if st.button("Add New Client"):
            st.session_state.show_new_client_form = True

    # Show new client form if requested
    if st.session_state.get('show_new_client_form', False):
        if render_client_form(db):
            st.session_state.show_new_client_form = False
            st.rerun()
        return

    # Continue with transcription only if client is selected
    if not selected_client:
        return

    # Create 2-column layout for timestamp checkbox and language selection
    st.subheader("Transcription Settings")
    col1, col2 = st.columns(2)

    with col1:
        # Add checkbox for timestamp option with default value set to False
        include_timestamps = st.checkbox("Include timestamps in transcription", value=False)

    with col2:
        # Add language selection
        languages = get_available_languages()
        target_language = st.selectbox(
            "Select translation language (optional)",
            options=[''] + list(languages.keys()),
            format_func=lambda x: 'No translation' if x == '' else f"{languages[x]} ({x})"
        )

    # Add upload mode selection
    upload_mode = st.radio("Upload Mode", ["Single File", "Bulk Directory Import"])

    if upload_mode == "Single File":
        # File uploader in its own row
        video_file = st.file_uploader("Upload your video file", 
                                    type=['mp4', 'avi', 'mov', 'mkv', 'wmv'])

        if video_file is not None and client_id:
            # Validate video format
            if not is_valid_video_format(video_file.name):
                st.error("Invalid video format. Please upload a supported video file.")
                return

            # Create a progress container and progress bar
            progress_container = st.container()
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with progress_container:
                try:
                    # Stage 1: Save uploaded file (10% of progress)
                    status_text.text("Saving uploaded file...")
                    file_extension = os.path.splitext(video_file.name)[1]
                    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as tmp_file:
                        tmp_file.write(video_file.read())
                        video_path = tmp_file.name
                    progress_bar.progress(10)
                    
                    # Process the video file
                    transcription = process_video(
                        video_path, client_id, include_timestamps, target_language,
                        languages, db, progress_container, progress_bar, status_text,
                        video_file.name
                    )

                    if transcription:
                        # Stage 5: Cleanup and finalization (last 10%)
                        status_text.text("Finalizing...")
                        os.unlink(video_path)
                        progress_bar.progress(100)
                        status_text.text("Processing completed!")
                        time.sleep(1)  # Brief pause to show completion
                        status_text.empty()  # Clear status text
                        progress_bar.empty()  # Clear progress bar

                        st.success("Processing completed!")
                        
                        # Display the generated transcript immediately
                        st.subheader("Generated Transcript")
                        st.text_area(
                            "Transcript",
                            value=transcription,
                            height=400,
                            disabled=True
                        )

                except Exception as e:
                    st.error(f"Error processing video: {str(e)}")
                    # Clean up temporary files in case of error
                    if 'video_path' in locals() and os.path.exists(video_path):
                        os.unlink(video_path)

    else:
        # Bulk directory import
        directory_path = st.text_input("Enter directory path containing video files")
        if directory_path and st.button("Process Directory"):
            if not os.path.exists(directory_path):
                st.error("Directory not found")
                return
                
            video_files = [f for f in os.listdir(directory_path) 
                          if is_valid_video_format(f)]
            if not video_files:
                st.error("No valid video files found in directory")
            else:
                total_files = len(video_files)
                st.info(f"Found {total_files} video files")
                
                # Overall progress bar
                overall_progress = st.progress(0)
                overall_status = st.empty()
                
                # Individual file progress
                file_progress = st.progress(0)
                file_status = st.empty()
                
                successful_files = 0
                for i, video_file in enumerate(video_files, 1):
                    overall_status.text(f"Processing file {i} of {total_files}: {video_file}")
                    video_path = os.path.join(directory_path, video_file)
                    
                    # Process the video file
                    success = process_video(
                        video_path, client_id, include_timestamps, target_language,
                        languages, db, st.container(), file_progress, file_status,
                        video_file
                    )
                    
                    if success:
                        successful_files += 1
                    
                    # Update overall progress
                    overall_progress.progress(i / total_files)
                    file_progress.empty()
                    file_status.empty()
                
                # Final status
                overall_status.text(
                    f"Processing completed: {successful_files} of {total_files} files processed successfully"
                )
                if successful_files < total_files:
                    st.warning(
                        f"Some files failed to process. {total_files - successful_files} files were skipped."
                    )
                else:
                    st.success("All files processed successfully!")

def main():
    # Initialize session state for navigation
    if 'page' not in st.session_state:
        st.session_state.page = "transcription"
    if 'show_new_client_form' not in st.session_state:
        st.session_state.show_new_client_form = False

    # Navigation sidebar
    with st.sidebar:
        st.image("assets/dragon.png", use_column_width=True)
        st.title("Video Transcription Agent")
        if st.button("Transcription Service", key="nav_trans"):
            st.session_state.page = "transcription"
            st.session_state.show_new_client_form = False
            st.rerun()
        if st.button("Client Management", key="nav_crm"):
            st.session_state.page = "crm"
            st.session_state.show_new_client_form = False
            st.rerun()

    # Render the appropriate page
    if st.session_state.page == "transcription":
        render_transcription_interface()
    else:
        render_crm_interface()

if __name__ == "__main__":
    main()
