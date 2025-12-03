import chromadb
import cohere
import os
from dotenv import load_dotenv
from data_loader import load_documents

load_dotenv()

# Initialize clients
co = cohere.Client(api_key=os.getenv("COHERE_API_KEY"))
chroma_client = chromadb.PersistentClient(path="./chroma_data")

# Load documents
documents = load_documents("data/holistic")
print(f"Loaded {len(documents)} documents")

# Create collection
collection = chroma_client.get_or_create_collection(
    name="holistic_knowledge",
    metadata={"description": "Holistic health and wellness knowledge base"}
)

# Embed and store documents
texts = [doc['content'] for doc in documents]
ids = [doc['id'] for doc in documents]
sources = [doc['source'] for doc in documents]

# Embed in batches (Cohere has rate limits)
batch_size = 96  # Cohere's max batch size
for i in range(0, len(texts), batch_size):
    batch_texts = texts[i:i+batch_size]
    batch_ids = ids[i:i+batch_size]
    batch_sources = sources[i:i+batch_size]
    
    # Get embeddings
    response = co.embed(
        texts=batch_texts,
        model="embed-english-v3.0",
        input_type="search_document"
    )
    embeddings = response.embeddings
    
    # Store in Chroma
    collection.add(
        embeddings=embeddings,
        documents=batch_texts,
        ids=batch_ids,
        metadatas=[{"source": s} for s in batch_sources]
    )
    
    print(f"Embedded batch {i//batch_size + 1}")

print("✅ All documents embedded and stored!")