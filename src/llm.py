from groq import Groq
from src.config import GROQ_API_KEY
import time
import logging

client = Groq(api_key=GROQ_API_KEY)
log = logging.getLogger(__name__)

def generate_response(query: str, context: str, user_context: str = None, conversation_history: str = None):
    """
    Generate response using LLM with optional user personalization.
    Returns: tuple(response_string, generation_time_seconds, cumulative_tokens_or_None, cumulative_cost_or_None)
    """
    start = time.time()

    # Build system prompt with conversational tone
    system_prompt = """You are Ombee AI, a friendly and knowledgeable health assistant specializing in holistic wellness and nutrition.

Your conversation style:
- Be warm, conversational, and natural (like chatting with a knowledgeable friend)
- Keep responses concise (2-4 sentences for simple questions, up to 2 short paragraphs for complex ones)
- Answer the specific question asked - don't over-explain
- Use a friendly, encouraging tone
- If asked follow-up questions, build on the previous conversation naturally
- Only provide detailed explanations when explicitly asked for more information

Your guidelines:
- Base answers on the provided context when available
- Never diagnose medical conditions
- For serious health concerns, recommend consulting a healthcare provider
- If the context doesn't have enough information, say so honestly and offer what you do know
- Cite sources only when making specific health claims

Remember: This is a conversation, not a lecture. Be helpful but conversational."""

    if user_context:
        system_prompt += f"""

User Profile: {user_context}
Use this to personalize responses naturally (e.g., suggest vegetarian options for vegetarians)."""

    # Build the prompt with conversation awareness
    if conversation_history:
        user_prompt = f"""Previous conversation:
{conversation_history}

Context from knowledge base:
{context}

User's current question: {query}

Respond naturally as if continuing a conversation. Keep it concise and conversational."""
    else:
        user_prompt = f"""Context from knowledge base:
{context}

User question: {query}

Provide a helpful, concise response. Keep it conversational and to-the-point."""

    try:
        # Generate response
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=300  # Reduced from 500 for more concise responses
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