from groq import Groq
from src.config import GROQ_API_KEY
import time
import logging

client = Groq(api_key=GROQ_API_KEY)
log = logging.getLogger(__name__)

def generate_response(query: str, context: str, user_profile: dict = None):
    """
    Generate response using LLM with retrieved context.
    Returns: tuple(response_string, generation_time_seconds, cumulative_tokens_or_None, cumulative_cost_or_None)
    """
    
    # Build system prompt
    system_prompt = """You are Ombee, a knowledgeable and empathetic AI health assistant specializing in holistic wellness, nutrition, and daily health longevity.

Your role:
- Provide evidence-based health and wellness guidance based on the provided context
- Be supportive, encouraging, and conversational
- Always remind users you are not a substitute for professional medical advice
- Cite the context when making specific health claims
- If the context doesn't contain relevant information, say so honestly

Important guidelines:
- NEVER diagnose medical conditions
- For serious health concerns, always recommend consulting a healthcare provider
- Base your advice primarily on the provided context
- Be friendly and approachable in tone
- Keep responses concise but informative (aim for 150-300 words)"""

    # Add user profile context if available
    profile_context = ""
    if user_profile and user_profile.get('conditions'):
        conditions = user_profile.get('conditions', [])
        if conditions:
            profile_context = f"\n\nUser's health background: {', '.join(conditions)}"
    
    # Build user message
    user_message = f"""Context from Ombee knowledge base:
{context}
{profile_context}

User question: {query}

Please provide a helpful, accurate response based primarily on the context above. If the context doesn't fully answer the question, acknowledge that and provide what information you can."""

    start = time.time()
    try:
        # Generate response
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        end = time.time()
        generation_time = end - start

        # Extract text
        text = ""
        try:
            text = response.choices[0].message.content
        except Exception:
            try:
                text = getattr(response, "text", "") or str(response)
            except Exception:
                text = ""

        # Try to extract usage metrics
        tokens = None
        cost = None
        try:
            usage = getattr(response, "usage", None) or getattr(response, "meta", None)
            if usage:
                tokens = usage.get("total_tokens") if isinstance(usage, dict) else getattr(usage, "total_tokens", None)
                cost = usage.get("estimated_cost") if isinstance(usage, dict) else getattr(usage, "estimated_cost", None)
        except Exception:
            pass

        return text, generation_time, tokens, cost

    except Exception as e:
        end = time.time()
        generation_time = end - start
        log.exception("LLM generation error")
        return f"I apologize, but I encountered an error generating a response. Please try again. Error: {str(e)}", generation_time, None, None