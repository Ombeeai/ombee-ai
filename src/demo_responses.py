"""
Demo responses for specific queries in non-holistic domains.
These are used to simulate responses from future AI agents (e.g., Finance, Telecom)
"""

def get_demo_response(query: str, domain: str) -> dict | None:
    """Return demo response if query matches demo patterns"""
    query_lower = query.lower()
    
    # Financial domain demos
    if domain == 'financial':
        if 'restaurant' in query_lower and any(word in query_lower for word in ['spend', 'spent', 'cost']):
            return {
                'response': """Based on your Ombee Finance account, here's your restaurant spending for last month:

**Total Restaurant Spending: $487.32**

Top locations:
• Chipotle - $142.50 (6 visits)
• Starbucks - $98.20 (14 visits)
• Olive Garden - $87.40 (2 visits)
• Local Café - $159.22 (8 visits)

This represents 18% of your monthly food budget. You're $87 over your dining out goal of $400/month.

💡 *Tip: Consider meal prepping 2-3 times per week to reduce dining costs.*

*Note: This is demo data. Full Ombee Finance integration coming Q2 2026.*""",
                'sources': ['Ombee Finance Demo Data'],
                'status': 'demo'
            }
        
        elif 'budget' in query_lower or 'spending' in query_lower:
            return {
                'response': """Here's your Ombee Finance overview for this month:

**Monthly Budget Status:**
• Total Budget: $3,500
• Spent So Far: $2,843 (81%)
• Remaining: $657

**Top Categories:**
• Housing: $1,200 (34%)
• Food & Dining: $687 (20%)
• Transportation: $423 (12%)
• Entertainment: $312 (9%)
• Utilities: $221 (6%)

You're on track to stay within budget! 🎉

*Note: This is demo data. Full Ombee Finance integration coming Q2 2026.*""",
                'sources': ['Ombee Finance Demo Data'],
                'status': 'demo'
            }
    
    # Telecom domain demos
    elif domain == 'telecom':
        if 'plan' in query_lower or 'phone plan' in query_lower:
            return {
                'response': """Your current Ombee Wireless plan:

**Plan Details:**
• Plan Name: Unlimited Plus
• Monthly Cost: $65/month
• Data: Unlimited 5G
• Hotspot: 50GB
• International: Free texting to 200+ countries

**This Month's Usage:**
• Data Used: 42.3 GB
• Hotspot Used: 8.2 GB
• Minutes: 847 min
• Texts: 1,234 messages

Your plan is working great for your usage! All within limits. ✅

*Note: This is demo data. Full Ombee Wireless integration coming Q2 2026.*""",
                'sources': ['Ombee Wireless Demo Data'],
                'status': 'demo'
            }
        
        elif 'data' in query_lower and 'usage' in query_lower:
            return {
                'response': """Your Ombee Wireless data usage this month:

**Data Breakdown:**
• Total Used: 42.3 GB
• Unlimited plan - no overage charges! ✅

**Usage by App:**
• Streaming (Netflix, YouTube): 18.4 GB
• Social Media: 12.8 GB
• Web Browsing: 7.2 GB
• Maps & Navigation: 2.1 GB
• Other: 1.8 GB

**Trends:**
You're using 15% more data than last month, mainly from video streaming.

*Note: This is demo data. Full Ombee Wireless integration coming Q2 2026.*""",
                'sources': ['Ombee Wireless Demo Data'],
                'status': 'demo'
            }
    
    return None

def get_coming_soon_message(domain: str, query: str) -> str:
    """Return coming soon message for domains in development"""
    
    domain_info = {
        'financial': {
            'name': 'Ombee Finance',
            'icon': '💰',
            'features': 'budget tracking, spending analysis, and financial insights'
        },
        'telecom': {
            'name': 'Ombee Wireless',
            'icon': '📱',
            'features': 'plan management, usage tracking, and billing information'
        }
    }
    
    info = domain_info.get(domain, {
        'name': domain.title(),
        'icon': '🔄',
        'features': 'specialized services'
    })
    
    return f"""{info['icon']} **{info['name']} - Coming Soon!**

Great question about {domain} services! This feature is currently in active development as part of Ombee AI Phase 2.

**What's Coming:**
{info['name']} will provide {info['features']}, all integrated with your personalized AI assistant.

**Current Status:**
The Holistic Health domain is live and ready to help with wellness, nutrition, and health questions!

**Launch Timeline:**
{info['name']} is planned for Q2 2026.

In the meantime, feel free to ask me anything about holistic health, nutrition, meditation, sleep, or wellness! 🧘‍♀️

*Stay tuned for updates on {info['name']}!*"""