from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio
from ..services.game_service import game_service
from ..game.constants import Color

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Dict[str, WebSocket]] = {}  # game_id -> {user_id: ws}
        self.user_connections: Dict[str, WebSocket] = {}  # user_id -> ws
    
    async def connect(self, websocket: WebSocket, game_id: str, user_id: str):
        """Connect a user to a game"""
        await websocket.accept()
        
        if game_id not in self.active_connections:
            self.active_connections[game_id] = {}
        
        self.active_connections[game_id][user_id] = websocket
        self.user_connections[user_id] = websocket
        
        # Send current game state
        game_state = game_service.get_game_state(game_id)
        if game_state:
            await self.send_personal_message(websocket, {
                "type": "game_state",
                "data": game_state
            })
    
    def disconnect(self, game_id: str, user_id: str):
        """Disconnect a user"""
        if game_id in self.active_connections:
            self.active_connections[game_id].pop(user_id, None)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
        
        self.user_connections.pop(user_id, None)
        
        # Handle player disconnection in game
        game_service.handle_player_disconnect(user_id)
    
    async def broadcast_to_game(self, game_id: str, message: dict, 
                               exclude: str = None):
        """Broadcast message to all players in a game"""
        if game_id not in self.active_connections:
            return
        
        for user_id, ws in self.active_connections[game_id].items():
            if user_id != exclude:
                try:
                    await ws.send_json(message)
                except Exception:
                    pass
    
    async def send_personal_message(self, websocket: WebSocket, message: dict):
        """Send message to specific user"""
        try:
            await websocket.send_json(message)
        except Exception:
            pass
    
    async def send_to_user(self, user_id: str, message: dict):
        """Send message to user by ID"""
        ws = self.user_connections.get(user_id)
        if ws:
            await self.send_personal_message(ws, message)
    
    def get_game_connections(self, game_id: str) -> int:
        """Get number of connected players in a game"""
        return len(self.active_connections.get(game_id, {}))

# Singleton instance
manager = ConnectionManager()

async def handle_websocket(websocket: WebSocket, game_id: str, user_id: str):
    """Handle WebSocket connection"""
    await manager.connect(websocket, game_id, user_id)
    
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            
            action = message.get("action")
            
            if action == "roll_dice":
                result = game_service.roll_dice(game_id)
                await manager.broadcast_to_game(game_id, {
                    "type": "dice_rolled",
                    "data": result
                })
                
                # If AI turn next, trigger it
                game = game_service.games.get(game_id)
                if game and game.players[game.current_turn].is_ai:
                    asyncio.create_task(handle_ai_turn_async(game_id))
            
            elif action == "make_move":
                token_id = message.get("tokenId")
                result = game_service.make_move(game_id, token_id)
                
                await manager.broadcast_to_game(game_id, {
                    "type": "move_made",
                    "data": result
                })
                
                # Send updated game state
                game_state = game_service.get_game_state(game_id)
                await manager.broadcast_to_game(game_id, {
                    "type": "game_state",
                    "data": game_state
                })
                
                # If AI turn next, trigger it
                game = game_service.games.get(game_id)
                if game and game.current_turn and \
                   game.phase.value != "finished" and \
                   game.players[game.current_turn].is_ai:
                    asyncio.create_task(handle_ai_turn_async(game_id))
            
            elif action == "chat_message":
                chat_msg = message.get("message", "")
                await manager.broadcast_to_game(game_id, {
                    "type": "chat",
                    "data": {
                        "userId": user_id,
                        "message": chat_msg,
                        "timestamp": asyncio.get_event_loop().time()
                    }
                })
            
            elif action == "ping":
                await manager.send_personal_message(websocket, {
                    "type": "pong"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(game_id, user_id)
        await manager.broadcast_to_game(game_id, {
            "type": "player_disconnected",
            "data": {"userId": user_id}
        })
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(game_id, user_id)

async def handle_ai_turn_async(game_id: str):
    """Handle AI turn and broadcast results"""
    game = game_service.games.get(game_id)
    if not game:
        return
    
    # Wait a moment
    await asyncio.sleep(1)
    
    # Roll dice
    result = game_service.roll_dice(game_id)
    await manager.broadcast_to_game(game_id, {
        "type": "dice_rolled",
        "data": result
    })
    
    # Make move if possible
    if game.phase.value == "moving":
        await asyncio.sleep(1)
        from ..services.ai_service import AIService
        ai_service = AIService()
        move = await ai_service.decide_move(game)
        
        if move is not None:
            move_result = game_service.make_move(game_id, move)
            await manager.broadcast_to_game(game_id, {
                "type": "move_made",
                "data": move_result
            })
    
    # Send updated state
    game_state = game_service.get_game_state(game_id)
    await manager.broadcast_to_game(game_id, {
        "type": "game_state",
        "data": game_state
    })