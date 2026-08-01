from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.routes import router as api_router
from .api.ws import ws_endpoint, games
from .game.state import GameState
from pydantic import BaseModel

app = FastAPI(title="Ludo AI")

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

app.include_router(api_router, prefix="/api")

@app.websocket("/ws/{game_id}")
async def websocket_endpoint(websocket, game_id: str):
    if game_id not in games:
        games[game_id] = GameState(game_id=game_id)
    await ws_endpoint(websocket, game_id, games[game_id])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)