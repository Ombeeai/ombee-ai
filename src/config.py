import streamlit as st

def get_secret(key, default=None):
    """
    Get secret from st.secrets
    """
    try:
        # Try Streamlit secrets first (for Streamlit Cloud)
        return st.secrets[key]
    except KeyError:
        # Provide error if a required key is missing
        if default is None:
            raise KeyError(f"Configuration key '{key}' not found in Streamlit secrets.")
        return default

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