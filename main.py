from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

from .services.game_service import game_service
from .api.websocket import router as websocket_router

app = FastAPI(title="Ludo Royale API")

# --- CORS Configuration ---
# This is the crucial part to fix the error.
# It allows your frontend (running on localhost:3000) to communicate with the backend.
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --------------------------

@app.post("/api/create-game", status_code=201)
async def create_game_endpoint(player_types: List[str]):
    # For simplicity, we'll use the first player type for the host.
    # In a real app, you'd have user authentication.
    host_name = player_types[0] if player_types else "Player 1"
    game_id = game_service.create_game(host_user_id=None, host_name=host_name)
    
    # Add other players (AI or placeholders)
    for pt in player_types[1:]:
        game_service.add_ai_player(game_id, ai_type=pt.split(" ")[0].lower())

    game_service.start_game(game_id)
    return {"game_id": game_id}

app.include_router(websocket_router)