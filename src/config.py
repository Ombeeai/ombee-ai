"""
Configuration management for Ombee AI application.
"""
import os
from dotenv import load_dotenv

load_dotenv()  # Load .env file if present

def get_env(key: str, default=None, required=False):
    """
    Get enviroment variable or raise error if required and not found.
    """
    value = os.getenv(key, default)
    if required and value is None:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value

# === Database Configuration ===
DATABASE_URL = get_env("DATABASE_URL", "sqlite:///./ombee.db")

# === Vector Database (Pinecone) Configuration ===
PINECONE_API_KEY = get_env("PINECONE_API_KEY",required=True)
PINECONE_ENVIRONMENT = get_env("PINECONE_ENVIRONMENT","us-east-1")
PINECONE_INDEX_NAME = get_env("PINECONE_INDEX_NAME","ombee-holistic")

# === Embeddings (Cohere) Configuration ===
COHERE_API_KEY = get_env("COHERE_API_KEY",required=True)

# === LLM (Groq) Configuration ===
GROQ_API_KEY = get_env("GROQ_API_KEY",required=True)

# === Monitoring (Arize Phoenix) Configuration ===
PHOENIX_API_KEY=get_env("PHOENIX_API_KEY")
PHOENIX_COLLECTOR_ENDPOINT=get_env("PHOENIX_COLLECTOR_ENDPOINT", "https://app.phoenix.arize.com")

# === Supabase Configuration ===
SUPABASE_URL = get_env("SUPABASE_URL")
SUPABASE_API_KEY = get_env("SUPABASE_API_KEY")
SUPABASE_PASSWORD= get_env("SUPABASE_PASSWORD")
ADMIN_PASSWORD_HASH = get_env("ADMIN_PASSWORD_HASH")

# === Application Settings ===
APP_NAME = "Ombee AI"
APP_VERSION = "1.0.0"
DEBUG = get_env("DEBUG", "false").lower() == "true"

# Print configuration status
if __name__ == "__main__":
    print("Ombee AI Configuration:")
    print(f"  Database: {DATABASE_URL}")
    print(f"  Pinecone Index: {PINECONE_INDEX_NAME}")
    print(f"  Pinecone API: {'Set' if PINECONE_API_KEY else 'Missing'}")
    print(f"  Cohere API: {'Set' if COHERE_API_KEY else 'Missing'}")
    print(f"  Groq API: {'Set' if GROQ_API_KEY else 'Missing'}")
    print(f"  Phoenix API: {'Set' if PHOENIX_API_KEY else 'Optional - monitoring disabled'}")
    print(f"  Debug Mode: {'Enabled' if DEBUG else 'Disabled'}")