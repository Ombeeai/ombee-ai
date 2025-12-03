from src.router import detect_domain
from src.retriever import retrieve_context
from src.llm import generate_response

print("🚀 Starting test script...")

# Test imports first
print("📦 Testing imports...")
try:
    from src.router import detect_domain
    print("✅ Router imported")
except Exception as e:
    print(f"❌ Router import failed: {e}")
    exit(1)

try:
    from src.retriever import retrieve_context
    print("✅ Retriever imported")
except Exception as e:
    print(f"❌ Retriever import failed: {e}")
    exit(1)

try:
    from src.llm import generate_response
    print("✅ LLM imported")
except Exception as e:
    print(f"❌ LLM import failed: {e}")
    exit(1)

print("\n" + "=" * 70)
print("🧪 Testing Ombee RAG System\n")

# Test queries
test_queries = [
    "What are some meditation techniques for beginners?",
]

for query in test_queries:
    print(f"\n📝 Query: {query}")
    print("-" * 70)
    
    # Test routing
    print("Testing router...", flush=True)
    try:
        domain, confidence = detect_domain(query)
        print(f"✅ Domain: {domain} (confidence: {confidence:.0%})")
    except Exception as e:
        print(f"❌ Router error: {e}")
        import traceback
        traceback.print_exc()
        continue
    
    # Test retrieval
    print("Testing retrieval...", flush=True)
    try:
        print("  → Calling retrieve_context()...", flush=True)
        context, sources = retrieve_context(query)
        print(f"  → Got response from retrieve_context()", flush=True)
        print(f"✅ Retrieved {len(sources)} sources")
        print(f"✅ Context length: {len(context)} characters")
        
        # Show a snippet of context
        if len(context) > 0:
            print(f"✅ Context preview: {context[:200]}...")
        else:
            print("⚠️  Context is empty!")
            
        if sources:
            print(f"✅ Sources found: {sources}")
        else:
            print("⚠️  No sources returned!")
            
    except Exception as e:
        print(f"❌ Retrieval error: {e}")
        import traceback
        traceback.print_exc()
        continue
    
    # Test LLM
    print("\nTesting LLM generation...", flush=True)
    try:
        print("  → Calling generate_response()...", flush=True)
        response = generate_response(query, context)
        print(f"  → Got response from generate_response()", flush=True)
        print(f"✅ Response generated: {len(response)} characters")
        print(f"\n💬 Response:\n{response}")
    except Exception as e:
        print(f"❌ LLM error: {e}")
        import traceback
        traceback.print_exc()
        continue
    
    if sources:
        print(f"\n📄 Sources: {', '.join(sources[:3])}")
    
    print("\n" + "=" * 70)

print("\n✅ Test complete!")