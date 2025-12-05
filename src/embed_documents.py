from pinecone import Pinecone, ServerlessSpec
import cohere
from src.config import PINECONE_API_KEY, COHERE_API_KEY
from data_loader import load_documents
import time

print("🚀 Starting Pinecone embedding process...")

# Initialize Pinecone
print("Initializing Pinecone...")
pc = Pinecone(api_key=PINECONE_API_KEY)
print("✅ Pinecone initialized")

# Initialize Cohere
print("Initializing Cohere...")
co = cohere.Client(api_key=COHERE_API_KEY)
print("✅ Cohere initialized")

# Load documents
print("\nLoading documents from data/holistic/...")
documents = load_documents("data/holistic")
print(f"✅ Loaded {len(documents)} documents")

if len(documents) == 0:
    print("❌ No documents found!")
    exit(1)

# Create or connect to index
index_name = "ombee-holistic"
print(f"\nChecking if index '{index_name}' exists...")

# Delete old index if exists
if index_name in pc.list_indexes().names():
    print("Found existing index, deleting...")
    pc.delete_index(index_name)
    print("✅ Old index deleted")
    time.sleep(1)

# Create new index (1024 dimensions for Cohere embed-english-v3.0)
print("Creating new index...")
pc.create_index(
    name=index_name,
    dimension=1024,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
print("✅ Index created (this may take a minute to initialize...)")

# Wait for index to be ready
time.sleep(5)

# Connect to index
index = pc.Index(index_name)
print(f"✅ Connected to index")

# Embed documents
print(f"\nEmbedding {len(documents)} documents...")
texts = [doc['content'] for doc in documents]
ids = [doc['id'] for doc in documents]
sources = [doc['source'] for doc in documents]

print("  → Calling Cohere API...")
response = co.embed(
    texts=texts,
    model="embed-english-v3.0",
    input_type="search_document"
)
embeddings = response.embeddings
print(f"  ✅ Got {len(embeddings)} embeddings")

# Upload to Pinecone
print(f"\nUploading {len(embeddings)} vectors to Pinecone...")

vectors_to_upsert = []
for i in range(len(embeddings)):
    vector_id = ids[i]
    vector_embedding = embeddings[i]
    vector_metadata = {
        "source": sources[i],
        "text": texts[i][:1000]  # Store first 1000 chars in metadata
    }
    
    vectors_to_upsert.append({
        "id": vector_id,
        "values": vector_embedding,
        "metadata": vector_metadata
    })
    print(f"  [{i+1}/{len(embeddings)}] Prepared: {sources[i]}")

print("\n  → Uploading to Pinecone...")
index.upsert(vectors=vectors_to_upsert)
print("  ✅ Upload complete!")

# Verify
time.sleep(2)
stats = index.describe_index_stats()
print(f"\n✅ Index stats: {stats['total_vector_count']} vectors stored")

print("\n🎉 All documents embedded and uploaded to Pinecone!")
print(f"\n🌐 View your index at: https://app.pinecone.io/")