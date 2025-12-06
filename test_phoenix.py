"""
Test script to verify Phoenix Cloud monitoring is working
"""

import time
from src.phoenix_monitoring import get_monitor

print("=" * 60)
print("Testing Phoenix Cloud Connection")
print("=" * 60)

# Get monitor instance
monitor = get_monitor()

if not monitor or not monitor.tracer:
    print("❌ Monitor not initialized properly")
    print("\nCheck:")
    print("1. PHOENIX_API_KEY is set in .env or src/config.py")
    print("2. PHOENIX_COLLECTOR_ENDPOINT is correct")
    exit(1)

print("\n✅ Monitor initialized successfully")
print(f"Project: {monitor.project_name}")
print(f"Endpoint: {monitor.phoenix_collector_endpoint}")

# Send test queries
print("\n" + "=" * 60)
print("Sending test traces...")
print("=" * 60)

test_cases = [
    {
        "query": "What are some meditation techniques?",
        "domain": "holistic",
        "confidence": 0.95,
        "response": "Here are some meditation techniques: breath awareness, body scan, and mindfulness meditation.",
        "sources": ["meditation_basics.txt", "mindfulness_guide.txt"],
        "latency": 2.3,
        "context": "Meditation is a practice where an individual uses a technique...",
        "status": "success"
    },
    {
        "query": "How much did I spend on food?",
        "domain": "financial",
        "confidence": 0.88,
        "response": "This is a demo response showing financial data.",
        "sources": ["demo_data"],
        "latency": 1.5,
        "status": "demo"
    },
    {
        "query": "Test error handling",
        "domain": "holistic",
        "confidence": 0.75,
        "response": "",
        "sources": [],
        "latency": 0.5,
        "error": "Test error message",
        "status": "error"
    }
]

for i, test_case in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] Logging: {test_case['query'][:40]}...")
    
    monitor.log_query(**test_case)
    
    # Small delay between traces
    time.sleep(0.5)

# Force flush all traces
print("\n" + "=" * 60)
print("Flushing traces to Phoenix Cloud...")
print("=" * 60)

if monitor.tracer_provider:
    monitor.tracer_provider.force_flush(timeout_millis=10000)
    print("✅ Flush complete")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
print("\n📊 Check your Phoenix dashboard:")
print("   https://app.phoenix.arize.com")
print(f"\n   Project: {monitor.project_name}")
print("\nNote: Traces may take 10-30 seconds to appear in the dashboard")
print("=" * 60)