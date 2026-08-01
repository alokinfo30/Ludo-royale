from .ai_client import generate_text

async def generate_commentary(player_name: str, move_desc: str, game_context: str) -> str:
    system = (
        "You are a funny, witty Ludo commentator who speaks in Hinglish (Hindi + English). "
        "Roast players gently, hype up big moves, use Indian pop culture references."
    )
    user = (
        f"Player: {player_name}\n"
        f"Move: {move_desc}\n"
        f"Game context: {game_context}\n"
        "Write a short one-line Hinglish commentary."
    )
    return generate_text(system, user).strip()