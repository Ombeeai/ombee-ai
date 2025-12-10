"""
Admin page for uploading documents to Pinecone
Access at: http://localhost:8501/admin_upload
"""

import streamlit as st
from pinecone import Pinecone
import cohere
import hashlib
from src.config import ADMIN_PASSWORD_HASH, PINECONE_API_KEY, COHERE_API_KEY, PINECONE_INDEX_NAME

def check_password():
    """Returns `True` if the user had the correct password."""
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if hashlib.sha256(st.session_state["admin_password"].encode()).hexdigest() == ADMIN_PASSWORD_HASH:
            st.session_state["admin_authenticated"] = True
            del st.session_state["admin_password"]
        else:
            st.session_state["admin_authenticated"] = False

    if "admin_authenticated" not in st.session_state:
        st.text_input(
            "Admin Password", 
            type="password", 
            on_change=password_entered, 
            key="admin_password"
        )
        return False
    elif not st.session_state["admin_authenticated"]:
        st.text_input(
            "Admin Password", 
            type="password", 
            on_change=password_entered, 
            key="admin_password"
        )
        st.error("😕 Incorrect password")
        return False
    else:
        return True

def process_and_upload_document(file_content, filename):
    """Process document and upload to Pinecone using Cohere embeddings"""
    try:
        # Initialize clients
        pc = Pinecone(api_key=PINECONE_API_KEY)
        co = cohere.Client(api_key=COHERE_API_KEY)
        
        # FIXED: Remove the second parameter - let Pinecone auto-detect the host
        index = pc.Index(PINECONE_INDEX_NAME)
        
        # Create document ID
        doc_id = filename.replace('.txt', '').replace(' ', '_').replace('.', '_')
        
        # Get embedding from Cohere
        response = co.embed(
            texts=[file_content],
            model="embed-english-v3.0",
            input_type="search_document"
        )
        embedding = response.embeddings[0]
        
        # Prepare vector
        vector = {
            "id": doc_id,
            "values": embedding,
            "metadata": {
                "source": filename,
                "text": file_content[:1000]  # Store first 1000 chars
            }
        }
        
        # Upload to Pinecone
        index.upsert(vectors=[vector])
        
        return True, None
    except Exception as e:
        return False, str(e)

# Page config
st.set_page_config(
    page_title="Admin - Document Upload",
    page_icon="🔒",
    layout="wide"
)

# Import auth functions
from src.auth import is_authenticated, is_admin, get_current_user

# Check if user is authenticated and is admin
if not is_authenticated():
    st.error("🔒 Please log in to access this page")
    st.stop()

if not is_admin():
    st.error("⛔ Access Denied - Admin privileges required")
    st.info("This page is only accessible to administrators.")
    if st.button("← Back to Main Page"):
        st.switch_page("app.py")
    st.stop()

# Authentication check (password protection as backup)
if not check_password():
    st.stop()

# Apply theme
from src.theme import apply_theme, apply_main_page_styles
apply_theme()
apply_main_page_styles()

# Header
st.title("🔒 Admin Document Upload")
st.markdown("Upload new documents to the Ombee knowledge base")
st.markdown("---")

# Main upload interface
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📤 Upload Documents")
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Choose text files to upload",
        type=['txt'],
        accept_multiple_files=True,
        help="Upload .txt files to add to the knowledge base"
    )
    
    if uploaded_files:
        st.success(f"✅ {len(uploaded_files)} file(s) selected")
        
        # Show file list
        with st.expander("📋 Selected Files"):
            for file in uploaded_files:
                st.write(f"• {file.name} ({file.size} bytes)")
        
        # Upload button
        if st.button("🚀 Upload to Pinecone", type="primary", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            success_count = 0
            error_count = 0
            
            for idx, file in enumerate(uploaded_files):
                status_text.text(f"Processing {file.name}...")
                
                # Read file content
                content = file.read().decode('utf-8')
                
                # Process and upload
                success, error = process_and_upload_document(content, file.name)
                
                if success:
                    success_count += 1
                    st.success(f"✅ Uploaded: {file.name}")
                else:
                    error_count += 1
                    st.error(f"❌ Failed: {file.name} - {error}")
                
                # Update progress
                progress_bar.progress((idx + 1) / len(uploaded_files))
            
            status_text.empty()
            progress_bar.empty()
            
            # Final summary
            st.markdown("---")
            st.markdown("### 📊 Upload Summary")
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("✅ Successful", success_count)
            with col_b:
                st.metric("❌ Failed", error_count)
            
            if success_count > 0:
                st.balloons()

with col2:
    st.markdown("### ℹ️ Instructions")
    st.markdown("""
    **How to upload:**
    1. Click 'Browse files' or drag & drop
    2. Select one or more .txt files
    3. Click 'Upload to Pinecone'
    4. Wait for processing to complete
    
    **Important:**
    - Only .txt files are supported
    - Files should be UTF-8 encoded
    - Large files may take longer to process
    - Each file creates one vector in Pinecone
    
    **File Naming:**
    Use descriptive names like:
    - `meditation_basics.txt`
    - `sleep_hygiene.txt`
    - `nutrition_guide.txt`
    """)
    
    st.markdown("---")
    
    # Index stats
    st.markdown("### 📊 Current Index Stats")
    
    try:
        pc = Pinecone(api_key=PINECONE_API_KEY)
        index = pc.Index(PINECONE_INDEX_NAME)
        stats = index.describe_index_stats()
        
        st.metric("Total Vectors", stats['total_vector_count'])
        st.metric("Index Dimension", stats.get('dimension', 'N/A'))
        
        with st.expander("🔍 View Details"):
            # Convert stats to JSON-serializable format
            if hasattr(stats, 'to_dict'):
                stats_dict = stats.to_dict()
            elif isinstance(stats, dict):
                stats_dict = stats
            else:
                stats_dict = dict(stats)
            st.json(stats_dict)
            
    except Exception as e:
        st.error(f"Could not fetch stats: {e}")

# Navigation buttons
st.markdown("---")
if st.button("← Back to Main Page", use_container_width=True):
        st.switch_page("app.py")