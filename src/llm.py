from groq import Groq
from src.config import GROQ_API_KEY
import time
import logging

client = Groq(api_key=GROQ_API_KEY)
log = logging.getLogger(__name__)

def generate_response(query: str, context: str, user_context: str = None):
    """
    Generate response using LLM with optional user personalization.
    Returns: tuple(response_string, generation_time_seconds, cumulative_tokens_or_None, cumulative_cost_or_None)
    """
    start = time.time()

    # Build system prompt with user context if available
    system_prompt = """You are Ombee AI, a knowledgeable and empathetic AI health assistant specializing in holistic wellness, nutrition, and daily health longevity.
    Provide helpful, accurate, and empathetic responses based on the provided context and user profile.

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


    if user_context:
        system_prompt += f"""

    USER PROFILE:
    {user_context}

    Important: Use this profile to personalize responses where relevant.
    For example:
    - If user is vegetarian and asks about protein, suggest plant-based options
    - If user's health goal is better sleep and they ask about exercise, mention evening routines
    - If user has dietary restrictions, ensure recommendations align with them
    - If user has specific health conditions, tailor advice to those conditions"""

    # Build the prompt
    user_prompt = f"""Context from knowledge base:
    {context}

    User question: {query}

    Please provide a helpful, accurate response based primarily on the context above. If the context doesn't fully answer the question, acknowledge that and provide what information you can."""

    if user_context:
        user_prompt += f"""
        Remember to consider the user's profile when generating your response."""

    try:
        # Generate response
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
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