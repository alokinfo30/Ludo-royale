from openai import OpenAI
from ..config import get_settings
import json
from typing import Optional, Dict, Any

class OpenRouterClient:
    """Client for OpenRouter API"""
    
    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key
        )
        self.model = settings.ai_model
    
    async def get_completion(self, prompt: str, 
                           system_prompt: str = None,
                           json_mode: bool = False) -> str:
        """Get completion from OpenRouter"""
        messages = []
        
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        messages.append({"role": "user", "content": prompt})
        
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 150
        }
        
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}
        
        try:
            response = self.client.chat.completions.create(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter API error: {e}")
            raise
    
    async def get_structured_response(self, prompt: str, 
                                     schema: Dict[str, Any]) -> Dict:
        """Get structured JSON response"""
        system_prompt = "You are a helpful assistant. Respond with valid JSON only."
        
        response = await self.get_completion(
            prompt=prompt,
            system_prompt=system_prompt,
            json_mode=True
        )
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback: extract JSON from response
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError(f"Could not parse JSON from response: {response}")