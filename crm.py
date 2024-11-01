import streamlit as st
from database import TranscriptionDB
import io
import time

def render_client_form(db, client_id=None):
    """Render form for adding/editing client details."""
    client = None if client_id is None else db.get_client_by_id(client_id)
    
    with st.form(key=f"client_form_{client_id if client_id else 'new'}"):
        st.subheader("Client Details")
        name = st.text_input("Name", value=client[1] if client else "")
        email = st.text_input("Email", value=client[2] if client else "")
        
        if st.form_submit_button("Save Client"):
            if not name or not email:
                st.error("Both name and email are required!")
                return False
            
            try:
                if client_id:
                    success = db.update_client(client_id, name, email)
                    if success:
                        st.success("Client updated successfully!")
                    else:
                        st.error("Failed to update client.")
                else:
                    client_id = db.add_client(name, email)
                    st.success("Client added successfully!")
                return True
            except Exception as e:
                st.error(f"Error: {str(e)}")
                return False
    return False

def export_transcriptions(transcriptions):
    """Create a formatted text file for bulk export."""
    output = io.StringIO()
    
    for filename, text, language, date in transcriptions:
        output.write(f"\n{'='*50}\n")
        output.write(f"File: {filename}\n")
        output.write(f"Date: {date}\n")
        output.write(f"Language: {language if language else 'Original'}\n")
        output.write(f"{'='*50}\n\n")
        output.write(text)
        output.write("\n\n")
    
    return output.getvalue()

def render_transcriptions_view(client_id):
    """Render the transcriptions view for a specific client."""
    db = TranscriptionDB()
    client = db.get_client_by_id(client_id)
    
    st.subheader(f"Transcriptions for {client[1]}")
    
    # Get all transcriptions
    transcriptions = db.get_client_transcriptions(client_id=client_id)
    
    if transcriptions:
        # Add bulk operations section
        st.write("### Bulk Operations")
        col1, col2 = st.columns(2)
        
        # Dictionary to store selected transcriptions
        if 'selected_transcriptions' not in st.session_state:
            st.session_state.selected_transcriptions = {}
        
        # Select all checkbox
        with col1:
            if st.checkbox("Select All", key="select_all"):
                for trans in transcriptions:
                    st.session_state.selected_transcriptions[trans[0]] = True
            else:
                st.session_state.selected_transcriptions = {}
        
        # Bulk action buttons
        with col2:
            bulk_action = st.selectbox(
                "Bulk Actions",
                ["Choose action...", "Download Selected", "Delete Selected"]
            )
        
        # Process bulk actions
        if bulk_action == "Delete Selected":
            selected_ids = [id for id, selected in st.session_state.selected_transcriptions.items() if selected]
            if selected_ids:
                if st.button("Confirm Delete Selected"):
                    success_count = 0
                    for trans_id in selected_ids:
                        if db.delete_transcription(trans_id):
                            success_count += 1
                    st.success(f"Successfully deleted {success_count} transcriptions")
                    st.session_state.selected_transcriptions = {}
                    time.sleep(1)
                    st.rerun()
        elif bulk_action == "Download Selected":
            selected_ids = [id for id, selected in st.session_state.selected_transcriptions.items() if selected]
            if selected_ids:
                # Get selected transcriptions
                selected_trans = [t for t in transcriptions if t[0] in selected_ids]
                formatted_trans = [(t[2], t[3], t[5], t[6]) for t in selected_trans]
                
                st.download_button(
                    label="Download Selected Transcriptions",
                    data=export_transcriptions(formatted_trans),
                    file_name=f"selected_transcriptions_{client[1]}.txt",
                    mime="text/plain"
                )
        
        # Display individual transcriptions with checkboxes
        for trans in transcriptions:
            trans_id, _, filename, text, has_timestamps, language, created_at = trans
            
            # Checkbox for selection
            is_selected = st.checkbox(
                f"Select {filename}",
                key=f"select_{trans_id}",
                value=st.session_state.selected_transcriptions.get(trans_id, False)
            )
            st.session_state.selected_transcriptions[trans_id] = is_selected
            
            with st.expander(f"{filename} - {created_at.split('.')[0]}"):
                # Editable metadata
                edited_language = st.text_input(
                    "Language",
                    value=language if language else "Original",
                    key=f"lang_{trans_id}"
                )
                
                st.write(f"Timestamps: {'Yes' if has_timestamps else 'No'}")
                st.text_area(
                    "Transcription",
                    text,
                    height=100,
                    key=f"trans_{trans_id}",
                    disabled=True
                )
                
                # Save metadata changes
                if edited_language != (language if language else "Original"):
                    if st.button("Save Changes", key=f"save_{trans_id}"):
                        # Update the transcription with new metadata
                        if db.update_transcription_metadata(trans_id, edited_language):
                            st.success("Changes saved successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to save changes.")
                
                # Individual download button
                col1, col2 = st.columns([1, 5])
                with col1:
                    st.download_button(
                        label="Download",
                        data=text,
                        file_name=f"transcription_{filename}_{trans_id}.txt",
                        mime="text/plain",
                        key=f"download_{trans_id}"
                    )
    else:
        st.info("No transcriptions found for this client.")
    
    if st.button("Back to Client List"):
        st.session_state.show_transcriptions = False
        st.rerun()

def render_client_management():
    """Render the client management section."""
    db = TranscriptionDB()
    
    st.subheader("Client Management")
    
    # Add new client button
    if st.button("Add New Client"):
        st.session_state.show_client_form = True
        st.session_state.selected_client = None
    
    # Show client form if requested
    if st.session_state.get('show_client_form', False):
        if render_client_form(db, st.session_state.get('selected_client')):
            st.session_state.show_client_form = False
            st.rerun()
    
    # Display clients table
    clients = db.get_all_clients()
    if clients:
        st.subheader("All Clients")
        for client in clients:
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 2, 2])
            with col1:
                st.write(client[1])  # Name
            with col2:
                st.write(client[2])  # Email
            with col3:
                if st.button("Edit", key=f"edit_{client[0]}"):
                    st.session_state.show_client_form = True
                    st.session_state.selected_client = client[0]
                    st.rerun()
            with col4:
                if st.button("View Transcriptions", key=f"view_{client[0]}"):
                    st.session_state.selected_client_id = client[0]
                    st.session_state.show_transcriptions = True
                    st.rerun()
            with col5:
                if st.button("Delete", key=f"delete_{client[0]}"):
                    st.session_state.confirm_delete = True
                    st.session_state.client_to_delete = client[0]
                    st.rerun()
    
    # Handle delete confirmation
    if st.session_state.get('confirm_delete', False):
        client_to_delete = st.session_state.client_to_delete
        client = db.get_client_by_id(client_to_delete)
        
        st.error("⚠️ Permanent Deletion Warning")
        st.warning(
            f"You are about to permanently delete the client '{client[1]}' and **ALL** their associated data:\n\n"
            "- All transcription records\n"
            "- All transcription texts and metadata\n"
            "- Client information and history\n\n"
            "**This action cannot be undone.** Are you sure you want to proceed?"
        )
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Permanently Delete"):
                if db.delete_client(client_to_delete):
                    st.success("Client and all associated data deleted successfully!")
                    st.session_state.confirm_delete = False
                    st.session_state.client_to_delete = None
                    st.rerun()
                else:
                    st.error("Failed to delete client.")
        with col2:
            if st.button("No, Cancel"):
                st.session_state.confirm_delete = False
                st.session_state.client_to_delete = None
                st.rerun()

def render_crm_interface():
    st.title("👥 Client Management Interface")
    
    # Initialize session state variables
    if 'show_client_form' not in st.session_state:
        st.session_state.show_client_form = False
    if 'show_transcriptions' not in st.session_state:
        st.session_state.show_transcriptions = False
    if 'confirm_delete' not in st.session_state:
        st.session_state.confirm_delete = False
    if 'client_to_delete' not in st.session_state:
        st.session_state.client_to_delete = None
    
    # Show either client management or transcriptions view
    if st.session_state.get('show_transcriptions', False):
        render_transcriptions_view(st.session_state.selected_client_id)
    else:
        render_client_management()
