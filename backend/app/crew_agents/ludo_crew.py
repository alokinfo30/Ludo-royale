import json
from typing import Optional

try:
    from crewai import Crew, Task
    from crewai.llm import LLM
except ImportError:  # pragma: no cover - optional dependency
    Crew = None
    Task = None
    LLM = None

from ..services.ai_client import generate_structured
from .personalities import AGGRESSOR, SAFE_PLAYER
from ..game.state import GameState
from ..game.player import Player, PlayerType

MOVE_SCHEMA = {
    "type": "object",
    "properties": {
        "token_id": {"type": "integer", "description": "Index 0-3 of token to move"},
        "chat_message": {"type": "string", "description": "Optional taunt or bluff message"}
    },
    "required": ["token_id"]
}

def _format_state_for_llm(state: GameState) -> str:
    """Convert game state to a textual description."""
    desc = ""
    for p in state.players.values():
        desc += f"{p.name} ({p.color.name}):\n"
        for i, t in enumerate(state.board.tokens[p.color]):
            if t.position.type == "home":
                desc += f"  Token {i}: Home\n"
            elif t.position.type == "base":
                desc += f"  Token {i}: Base\n"
            elif t.position.type == "home_stretch":
                desc += f"  Token {i}: Home stretch step {t.position.index}\n"
            else:
                desc += f"  Token {i}: Track {t.position.index}\n"
    desc += f"Current dice roll: {state.dice_value}\n"
    desc += f"Current player: {state.current_player().name}\n"
    return desc

async def decide_ai_move(state: GameState) -> dict:
    """Choose an AI move, using CrewAI when available and a local heuristic otherwise."""
    if not state.valid_moves:
        return {"token_id": 0}

    player = state.current_player()
    if "Aggressor" in player.name:
        agent = AGGRESSOR
    else:
        agent = SAFE_PLAYER

    if Crew is not None and Task is not None and LLM is not None:
        system = "You are an AI Ludo player. Choose the best token to move from valid moves."
        user = f"Game state:\n{_format_state_for_llm(state)}\nRespond with a JSON indicating token_id."

        task = Task(
            description="Decide which token to move.",
            expected_output="JSON with token_id and optional chat_message.",
            agent=agent,
        )
        crew = Crew(
            agents=[agent],
            tasks=[task],
            verbose=False,
        )
        from ..config import get_settings
        settings = get_settings()
        agent.llm = LLM(
            model=f"openai/{settings.model_name}",
            base_url=settings.openrouter_base_url,
            api_key=settings.openrouter_api_key,
            temperature=0.3,
        )

        result = crew.kickoff()
        output = result.raw if hasattr(result, 'raw') else str(result)
        try:
            return json.loads(output)
        except json.JSONDecodeError:
            import re
            match = re.search(r'\{.*\}', output, re.DOTALL)
            if match:
                return json.loads(match.group())

    try:
        response = await generate_structured(
            f"Choose the best token to move for Ludo. Valid moves: {state.valid_moves}",
            {"token_id": "integer"},
        )
        token_id = response.get("token_id", 0)
        if 0 <= token_id < 4:
            return {"token_id": token_id}
    except Exception:
        pass

    return {"token_id": state.valid_moves[0][0].id}