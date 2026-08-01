from fastapi import APIRouter
from pydantic import BaseModel
from ..game.state import GameState
from ..game.player import Player, PlayerType, Token
from ..game.board import Color, Cell
from ..services.theme_generator import generate_theme

router = APIRouter()

class CreateGameRequest(BaseModel):
    player_names: list[str]  # e.g. ["Human", "Aggressor AI", "Safe AI"]
    human_color: str = "RED"

class ThemeRequest(BaseModel):
    prompt: str

@router.post("/create-game")
async def create_game(req: CreateGameRequest):
    # Create players
    colors = list(Color)
    players = []
    for i, name in enumerate(req.player_names):
        color = colors[i % len(colors)]
        ptype = PlayerType.HUMAN if i == 0 else PlayerType.AI  # first is human
        tokens = [Token(id=j, color=color, position=Cell()) for j in range(4)]
        player = Player(name=name, color=color, type=ptype, tokens=tokens)
        players.append(player)

    state = GameState(players=players)
    game_id = state.game_id
    # Store in global dict (simplified)
    from .ws import games
    games[game_id] = state
    return {"game_id": game_id, "message": "Game created"}

@router.post("/generate-theme")
async def theme_generator_endpoint(req: ThemeRequest):
    theme = await generate_theme(req.prompt)
    return {"theme": theme}