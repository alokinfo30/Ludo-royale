from .ai_client import generate_structured

THEME_SCHEMA = {
    "type": "object",
    "properties": {
        "boardBackground": {"type": "string", "description": "CSS gradient or color"},
        "homePathColors": {
            "type": "object",
            "properties": {
                "RED": {"type": "string"},
                "GREEN": {"type": "string"},
                "YELLOW": {"type": "string"},
                "BLUE": {"type": "string"}
            },
            "required": ["RED","GREEN","YELLOW","BLUE"]
        },
        "tokenColors": {
            "type": "object",
            "properties": {
                "RED": {"type": "string"},
                "GREEN": {"type": "string"},
                "YELLOW": {"type": "string"},
                "BLUE": {"type": "string"}
            },
            "required": ["RED","GREEN","YELLOW","BLUE"]
        },
        "diceColor": {"type": "string"},
        "font": {"type": "string"}
    },
    "required": ["boardBackground","homePathColors","tokenColors","diceColor"]
}

async def generate_theme(prompt: str) -> dict:
    system = "You are a creative board game theme designer. Output a JSON theme matching the schema."
    user = f"Create a Ludo board theme inspired by: {prompt}. Use vibrant colors, CSS gradients, and modern style."
    try:
        return generate_structured(system, user, THEME_SCHEMA)
    except Exception:
        return {
            "boardBackground": "linear-gradient(135deg, #1f2937 0%, #111827 100%)",
            "homePathColors": {
                "RED": "#ef4444",
                "GREEN": "#22c55e",
                "YELLOW": "#facc15",
                "BLUE": "#3b82f6"
            },
            "tokenColors": {
                "RED": "#ef4444",
                "GREEN": "#22c55e",
                "YELLOW": "#facc15",
                "BLUE": "#3b82f6"
            },
            "diceColor": "#ffffff",
            "font": "Inter, sans-serif"
        }