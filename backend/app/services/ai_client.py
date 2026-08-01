import json
import logging
from openai import OpenAI
from typing import Optional, Dict, Any
from ..config import get_settings

settings = get_settings()
client = OpenAI(
    base_url=settings.openrouter_base_url,
    api_key=settings.openrouter_api_key,
)

def generate_text(
    system_prompt: str,
    user_prompt: str,
    json_schema: Optional[Dict[str, Any]] = None,
    temperature: float = 0.7,
) -> str:
    """
    Call OpenRouter. If json_schema provided, try to use native response_format.
    Otherwise plain text. Returns content string.
    """
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]
    kwargs = {
        "model": settings.model_name,
        "messages": messages,
        "temperature": temperature,
    }
    if json_schema:
        kwargs["response_format"] = {
            "type": "json_schema",
            "json_schema": {
                "name": "output",
                "strict": True,
                "schema": json_schema,
            },
        }
    try:
        response = client.chat.completions.create(**kwargs)
        content = response.choices[0].message.content
        return content
    except Exception as e:
        logging.error(f"OpenRouter call failed: {e}")
        raise

def generate_structured(
    system_prompt: str,
    user_prompt: str,
    json_schema: Dict[str, Any],
) -> dict:
    """
    Returns parsed JSON dict. Falls back to manual parsing if schema not supported.
    """
    raw = generate_text(system_prompt, user_prompt, json_schema)
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # Fallback: try to extract JSON from markdown
        import re
        match = re.search(r'```json\s*(.*?)\s*```', raw, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        # Try to parse raw directly if it's JSON
        raise ValueError(f"Could not parse JSON from response: {raw}")