DEMO_RESPONSES = {
    "how much did i spend on restaurants last month": {
        "domain": "financial",
        "response": """Based on your linked Ombee Finance account:

    **October Restaurant Spending: $487.23**

    - 15 transactions
    - Most frequent: Chipotle (4 visits, $52.60 total)
    - Largest single purchase: Ruth's Chris ($142.50)
    - Average per transaction: $32.48

    📊 This is 23% above your $400 monthly budget.

    💡 **Suggestion:** Reducing to 12 restaurant visits per month could save you ~$87/month. Would you like budget-friendly meal prep ideas that align with your health goals?

    *[Demo data - Ombee Finance integration coming in Phase 2]*""",
            "sources": ["Ombee Finance - Demo Data"],
            "status": "demo"
        },
        
        "what's my current phone plan": {
            "domain": "telecom",
            "response": """Based on your Ombee Wireless account:

    **Current Plan: Unlimited Plus**
    - Monthly base cost: $80.00
    - Data: Unlimited 5G nationwide
    - Hotspot: 30GB high-speed
    - International: Talk & Text to Mexico/Canada included

    **Device Payment: iPhone 14 Pro (256GB)**
    - Remaining balance: $533.32
    - Monthly payment: $33.33
    - Payments remaining: 16 months

    **Total Monthly Bill: ~$127.43** (including taxes & fees)

    *[Demo data - Ombee Wireless integration coming in Phase 2]*""",
            "sources": ["Ombee Wireless - Demo Data"],
            "status": "demo"
        },
        
        "what's my data usage this month": {
            "domain": "telecom",
            "response": """I've identified your question about mobile data usage.

    Our **Ombee Wireless AI agent** is being integrated and will provide:
    - Real-time data usage tracking
    - Usage alerts and recommendations
    - Data optimization tips
    - Plan upgrade suggestions if needed

    **Expected launch:** Phase 2 (Q1 2025)

    For now, I'm here to help with holistic wellness topics! Ask me about nutrition, meditation, exercise, or managing health conditions like high blood pressure.""",
            "sources": [],
            "status": "coming-soon"
    }
}

def get_demo_response(query: str, domain: str = None) -> dict:
    """Check if query has a predefined demo response."""
    query_lower = query.lower().strip()
    return DEMO_RESPONSES.get(query_lower)

def get_coming_soon_message(domain: str, query: str) -> str:
    """Generate coming soon message for non-demo queries in non-holistic domains."""
    
    messages = {
        'financial': f"""I can see you're asking about financial information: "{query}"

        Our **Ombee Finance AI agent** is currently in development and will provide:
        - Personal budget tracking and recommendations
        - Spending pattern analysis and insights
        - Bill payment optimization
        - Savings goal tracking
        - Integration with your Ombee Finance account

        **Expected launch:** Phase 2 (Q1 2025)

        In the meantime, I'm fully operational for holistic health and wellness questions! Try asking about nutrition, meditation, exercise, sleep, stress management, or managing chronic health conditions.""",
                
                'telecom': f"""I've identified your question about mobile/telecom: "{query}"

        Our **Ombee Wireless AI agent** is being integrated and will offer:
        - Ombee Wireless account insights
        - Bill analysis and payment assistance
        - Data usage monitoring and optimization
        - Plan recommendations and upgrades
        - Network troubleshooting support

        **Expected launch:** Phase 2 (Q1 2025)

        For now, I'm here to help with holistic wellness topics! Ask me about healthy eating, stress management, sleep optimization, exercise guidance, or nutrition for specific health conditions."""
    }
    
    return messages.get(domain, "This feature is coming soon! For now, I can help with holistic health and wellness questions.")