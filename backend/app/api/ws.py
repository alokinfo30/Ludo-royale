from fastapi import WebSocket, WebSocketDisconnect
from ..game.state import GameState
from ..game.logic import get_valid_moves, apply_move
from ..services.agent_service import execute_ai_turn
import asyncio
import json
from typing import Dict

games: Dict[str, GameState] = {}

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, game_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[game_id] = websocket

    def disconnect(self, game_id: str):
        self.active_connections.pop(game_id, None)

    async def send_state(self, game_id: str, state: GameState):
        ws = self.active_connections.get(game_id)
        if ws:
            await ws.send_text(json.dumps({"type": "state", "payload": state.to_dict()}))

async def ws_endpoint(websocket: WebSocket, game_id: str, state: GameState):
    await manager.connect(game_id, websocket)
    try:
        if state:
            await manager.send_state(game_id, state)

        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            action = message.get("action")
            if not state:
                await websocket.send_text(json.dumps({"error": "Game not found"}))
                continue

            if action == "roll_dice":
                # Human player's turn: roll dice and send valid moves
                from ..game.logic import roll_and_set_dice
                dice = roll_and_set_dice(state)
                moves = get_valid_moves(state)
                await manager.send_state(game_id, state)
                await manager.send_message(game_id, {
                    "dice": dice,
                    "valid_moves": [
                        {"token_id": t.id, "target": serialize_pos(target)} for t, target in moves
                    ]
                })

            elif action == "move_token":
                token_id = int(message.get("token_id"))
                target_data = message.get("target")
                # Find token and target
                player = state.current_player()
                token = player.tokens[token_id]
                # Reconstruct target cell
                target_cell = Cell()
                if target_data["type"] == "track":
                    target_cell = Cell(track_index=target_data["index"])
                elif target_data["type"] == "home_stretch":
                    target_cell = Cell(track_index=target_data["step"], color=Color[target_data["color"]])
                # Apply move
                apply_move(state, token, target_cell)
                # Generate commentary for human move
                move_desc = f"Moved token {token_id} to {target_cell}"
                from ..services.commentary import generate_commentary
                commentary = await generate_commentary(player.name, move_desc, f"Dice: {state.dice_value}")
                await manager.send_message(game_id, {"commentary": commentary})
                # Next turn
                state.next_player()
                await manager.send_state(game_id, state)

                # If next player is AI, handle automatically
                while state and state.current_player().type == "AI" and not state.game_over:
                    result = await execute_ai_turn(state)
                    await manager.send_state(game_id, state)
                    if result.get("commentary"):
                        await manager.send_message(game_id, {"commentary": result["commentary"]})
                    await asyncio.sleep(1.5)  # pacing
    except WebSocketDisconnect:
        manager.disconnect(game_id)

def serialize_pos(target):
    if target.is_base():
        return {"type": "base"}
    if target.is_home_stretch():
        return {"type": "home_stretch", "step": target.track_index, "color": target.color.name}
    return {"type": "track", "index": target.track_index}