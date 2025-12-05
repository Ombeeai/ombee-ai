from pinecone import Pinecone
import cohere
from src.config import PINECONE_API_KEY, COHERE_API_KEY
from typing import Tuple, List

print("🔧 Initializing Pinecone retriever...")

# Initialize Pinecone
try:
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index("ombee-holistic")
    print("✅ Pinecone connected")
except Exception as e:
    print(f"❌ Pinecone initialization failed: {e}")
    index = None

# Initialize Cohere
try:
    co = cohere.Client(api_key=COHERE_API_KEY)
    print("✅ Cohere connected")
except Exception as e:
    print(f"❌ Cohere initialization failed: {e}")
    co = None

def retrieve_context(query: str, n_results: int = 5) -> Tuple[str, List[str]]:
    """
    Retrieve relevant context for a query from Pinecone.
    Returns: (context_string, list_of_sources)
    """
    print(f"  🔍 Retrieving context from Pinecone...")
    
    if index is None:
        print("  ❌ Pinecone index not available!")
        return "Error: Pinecone not initialized. Check API key.", []
    
    if co is None:
        print("  ❌ Cohere client not available!")
        return "Error: Cohere not initialized.", []
    
    try:
        # Embed the query
        print("  → Embedding query...")
        query_embedding = co.embed(
            texts=[query],
            model="embed-english-v3.0",
            input_type="search_query"
        ).embeddings[0]
        print(f"  ✅ Query embedded")
        
        # Search Pinecone
        print("  → Searching Pinecone...")
        results = index.query(
            vector=query_embedding,
            top_k=n_results,
            include_metadata=True
        )
        print(f"  ✅ Found {len(results['matches'])} results")
        
        # Extract context and sources
        contexts = []
        sources = []
        
        for match in results['matches']:
            text = match['metadata'].get('text', '')
            source = match['metadata'].get('source', 'Unknown')
            score = match['score']
            
            contexts.append(text)
            sources.append(f"{source} (score: {score:.2f})")
            print(f"    • {source}: {score:.2f}")
        
        if contexts:
            context = "\n\n---\n\n".join(contexts)
        else:
            context = "No relevant information found."
        
        return context, sources
    
    except Exception as e:
        print(f"  ❌ Error during retrieval: {e}")
        import traceback
        traceback.print_exc()
        return f"Error: {str(e)}", []