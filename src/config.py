import streamlit as st
import os
from dotenv import load_dotenv

# Load .env for local development
load_dotenv()

def get_secret(key, default=None):
    """
    Get secret from Streamlit Cloud secrets or environment variables.
    Works in both local and deployed environments.
    """
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        return st.secrets[key]
    except (KeyError, FileNotFoundError):
        # Fall back to environment variables (for local .env)
        return os.getenv(key, default)

# API Keys
PINECONE_API_KEY = get_secret("PINECONE_API_KEY")
PINECONE_ENVIRONMENT = get_secret("PINECONE_ENVIRONMENT")
PINECONE_INDEX_NAME = get_secret("PINECONE_INDEX_NAME")
COHERE_API_KEY = get_secret("COHERE_API_KEY")
GROQ_API_KEY = get_secret("GROQ_API_KEY")
PHOENIX_API_KEY=get_secret("PHOENIX_API_KEY")
PHOENIX_COLLECTOR_ENDPOINT=get_secret("PHOENIX_COLLECTOR_ENDPOINT", "https://app.phoenix.arize.com")
SUPABASE_URL = get_secret("SUPABASE_URL")
SUPABASE_API_KEY = get_secret("SUPABASE_API_KEY")
ADMIN_PASSWORD_HASH = get_secret("ADMIN_PASSWORD_HASH")