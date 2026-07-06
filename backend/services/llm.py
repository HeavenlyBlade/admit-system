"""
LLM service for response generation using Groq API.
Implements grounded generation with fallback mechanism.
"""
from typing import List
import os
import logging
from groq import Groq

from services.retrieval import KBMatch

logger = logging.getLogger(__name__)

# Groq API configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    logger.warning("GROQ_API_KEY not set, LLM service will not function")

# Initialize Groq client lazily
_groq_client = None


def get_groq_client():
    """Get or initialize Groq client lazily"""
    global _groq_client
    if _groq_client is None:
        if not GROQ_API_KEY:
            raise RuntimeError("Groq API client not initialized (missing API key)")
        _groq_client = Groq(api_key=GROQ_API_KEY)
    return _groq_client

# LLM parameters
MODEL_NAME = "llama-3.1-8b-instant"  # Fast, good quality
TEMPERATURE = 0.3  # Low for factual consistency
MAX_TOKENS = 256


def build_prompt(matches: List[KBMatch], query: str) -> str:
    """
    Build grounded prompt with retrieved KB context.
    
    Args:
        matches: List of KB matches with similarity scores
        query: User query
        
    Returns:
        str: Formatted prompt for LLM
    """
    # System instructions
    system_msg = """You are ADMIT, St. Anthony College of Ligao's (SACLI) admissions assistant.

CRITICAL RULES:
- Answer ONLY using the context provided below
- If the context doesn't fully answer the question, acknowledge this clearly
- Suggest contacting the appropriate office when needed:
  * Registrar's Office for admissions and enrollment
  * Scholarship Office for financial aid
  * Department offices for program-specific questions
- Be concise, warm, and helpful
- Use bullet points for lists
- Never make up information not in the context"""
    
    # Build context from matches
    context_parts = []
    for i, match in enumerate(matches[:5], 1):  # Use top 5
        context_parts.append(f"[Context {i}]")
        context_parts.append(f"Title: {match.title}")
        if match.category:
            context_parts.append(f"Category: {match.category.name} ({match.category.department})")
        context_parts.append(f"Content: {match.content}")
        context_parts.append("")  # Blank line
    
    context = "\n".join(context_parts)
    
    # Complete prompt
    prompt = f"""{system_msg}

CONTEXT:
{context}

QUESTION: {query}

ANSWER (be concise and helpful):"""
    
    return prompt


def validate_response(response: str) -> bool:
    """
    Check if response contains hallucination indicators.
    
    Args:
        response: LLM generated response
        
    Returns:
        bool: True if response looks valid, False if hallucination detected
    """
    # Hallucination indicators
    hallucination_phrases = [
        "i think",
        "i believe",
        "probably",
        "my opinion",
        "i'm not sure",
        "as far as i know",
        "it seems",
    ]
    
    response_lower = response.lower()
    
    for phrase in hallucination_phrases:
        if phrase in response_lower:
            logger.warning(f"Potential hallucination detected: '{phrase}' in response")
            return False
    
    return True


def generate_response(matches: List[KBMatch], query: str) -> str:
    """
    Generate response using Groq API with grounded prompt.
    """
    client = get_groq_client()
    prompt = build_prompt(matches, query)

    try:
        logger.info(f"Calling Groq API (model: {MODEL_NAME})")
        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            top_p=0.9,
            stop=["\n\nQuestion:", "\n\nCONTEXT:"],
        )
        response = completion.choices[0].message.content.strip()

        if not validate_response(response):
            logger.warning("Response failed validation, using fallback")
            return build_fallback_message(query)

        logger.info(f"Generated response ({len(response)} chars)")
        return response

    except Exception as e:
        logger.error(f"Groq API error: {str(e)}")
        raise RuntimeError(f"LLM generation failed: {str(e)}")


def build_fallback_message(query: str) -> str:
    """
    Build fallback message for out-of-scope queries.
    
    Args:
        query: User query (for context-based office suggestion)
        
    Returns:
        str: Fallback message with office contact information
    """
    # Simple keyword matching for office suggestion
    query_lower = query.lower()
    
    if any(word in query_lower for word in ["scholarship", "financial", "aid", "grant"]):
        office = "Scholarship Office"
        contact = "scholarship@sacli.edu.ph"
    elif any(word in query_lower for word in ["program", "course", "curriculum", "subject"]):
        office = "Department Office"
        contact = "programs@sacli.edu.ph"
    elif any(word in query_lower for word in ["admission", "enroll", "register", "requirements"]):
        office = "Registrar's Office"
        contact = "registrar@sacli.edu.ph"
    else:
        office = "Admissions Office"
        contact = "admissions@sacli.edu.ph"
    
    message = f"""I don't have specific information about that in my knowledge base.

For assistance with your question, please contact the **{office}**:
📧 Email: {contact}
📞 Phone: (052) 485-1234
🏫 Visit: SACLI Main Campus

Office Hours: Monday-Friday, 8:00 AM - 5:00 PM

You can also visit our campus in person during office hours for personalized assistance."""
    
    return message


def infer_department_from_query(query: str) -> str:
    """
    Infer department from query keywords (for future use).
    
    Args:
        query: User query
        
    Returns:
        str: Department code (IBED, SHS, HED, TESDA, GENERAL)
    """
    query_lower = query.lower()
    
    if "ibed" in query_lower or "basic education" in query_lower:
        return "IBED"
    elif "shs" in query_lower or "senior high" in query_lower:
        return "SHS"
    elif "hed" in query_lower or "college" in query_lower or "higher education" in query_lower:
        return "HED"
    elif "tesda" in query_lower or "technical" in query_lower or "vocational" in query_lower:
        return "TESDA"
    else:
        return "GENERAL"
