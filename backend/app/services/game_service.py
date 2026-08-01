from typing import Dict, Optional, List
import asyncio
import random
import string
from ..game.state import GameState, GamePhase
from ..game.constants import Color
from ..game.board import LudoBoard
from ..game.rules import GameRules
from .ai_service import AIService

class GameService:
    """Manages all game instances and logic"""
    
    def __init__(self):
        self.games: Dict[str, GameState] = {}
        self.player_games: Dict[str, str] = {}  # user_id -> game_id
        self.ai_service = AIService()
        self._cleanup_task = None
    
    def create_game(self, host_user_id: Optional[str], 
                   host_name: str, game_type: str = "online") -> str:
        """Create a new game"""
        game_id = self._generate_game_id()
        game = GameState(game_id=game_id)
        
        # Add host as first player
        game.add_player(host_user_id, host_name, Color.RED)
        
        self.games[game_id] = game
        if host_user_id:
            self.player_games[host_user_id] = game_id
        
        return game_id
    
    def join_game(self, game_id: str, user_id: Optional[str], 
                  name: str) -> Optional[Color]:
        """Join an existing game"""
        game = self.games.get(game_id)
        if not game or game.phase != GamePhase.WAITING:
            return None
        
        # Assign next available color
        for color in [Color.GREEN, Color.YELLOW, Color.BLUE]:
            if color not in game.players:
                game.add_player(user_id, name, color)
                if user_id:
                    self.player_games[user_id] = game_id
                return color
        
        return None
    
    def add_ai_player(self, game_id: str, ai_type: str = "balanced") -> bool:
        """Add an AI player to the game"""
        game = self.games.get(game_id)
        if not game:
            return False
        
        # Find available color
        for color in Color:
            if color not in game.players:
                ai_name = self.ai_service.get_ai_name(ai_type, color)
                game.add_player(None, ai_name, color, is_ai=True)
                return True
        
        return False
    
    def start_game(self, game_id: str) -> bool:
        """Start the game if enough players"""
        game = self.games.get(game_id)
        if not game:
            return False
        
        # Fill remaining slots with AI if needed
        if len(game.players) < 2:
            for _ in range(2 - len(game.players)):
                self.add_ai_player(game_id)
        
        # Start the game
        game.start_turn()
        game.phase = GamePhase.ROLLING
        
        # If first player is AI, trigger AI turn
        if game.players[game.current_turn].is_ai:
            asyncio.create_task(self._handle_ai_turn(game_id))
        
        return True
    
    def roll_dice(self, game_id: str) -> dict:
        """Handle dice roll"""
        game = self.games.get(game_id)
        if not game or game.phase != GamePhase.ROLLING:
            return {"error": "Invalid game state"}
        
        dice_value = game.roll_dice()
        
        result = {
            "diceValue": dice_value,
            "phase": game.phase.value,
            "validMoves": game.valid_moves,
            "consecutiveSixes": game.players[game.current_turn].consecutive_sixes
        }
        
        # If no valid moves, auto-skip
        if game.phase == GamePhase.ROLLING:
            result["message"] = "No valid moves, turn skipped"
        
        return result
    
    def make_move(self, game_id: str, token_id: int) -> dict:
        """Make a move"""
        game = self.games.get(game_id)
        if not game or game.phase != GamePhase.MOVING:
            return {"error": "Invalid game state"}
        
        try:
            result = game.make_move(token_id)
            return result
        except ValueError as e:
            return {"error": str(e)}
    
    def handle_player_disconnect(self, user_id: str) -> Optional[str]:
        """Handle player disconnection"""
        game_id = self.player_games.get(user_id)
        if not game_id:
            return None
        
        game = self.games.get(game_id)
        if not game:
            return None
        
        # Find player and convert to AI
        for color, player in game.players.items():
            if player.user_id == user_id:
                game.remove_player(color)
                # Start AI turn if it's this player's turn
                if game.current_turn == color:
                    asyncio.create_task(self._handle_ai_turn(game_id))
                return game_id
        
        return None
    
    async def _handle_ai_turn(self, game_id: str):
        """Handle AI player turn"""
        game = self.games.get(game_id)
        if not game:
            return
        
        # Wait a moment to simulate thinking
        await asyncio.sleep(1.5)
        
        # Roll dice
        self.roll_dice(game_id)
        
        # If there are valid moves, make one
        if game.phase == GamePhase.MOVING:
            # Get AI decision
            move = await self.ai_service.decide_move(game)
            if move is not None:
                result = self.make_move(game_id, move)
                
                # If AI got extra turn, continue
                if result.get("extraTurn") and game.phase != GamePhase.FINISHED:
                    await asyncio.sleep(1)
                    await self._handle_ai_turn(game_id)
    
    def get_game_state(self, game_id: str) -> Optional[dict]:
        """Get current game state"""
        game = self.games.get(game_id)
        if not game:
            return None
        return game.to_dict()
    
    def _generate_game_id(self) -> str:
        """Generate unique game ID"""
        while True:
            game_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if game_id not in self.games:
                return game_id
    
    async def cleanup_abandoned_games(self):
        """Clean up abandoned games"""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            current_time = asyncio.get_event_loop().time()
            to_remove = []
            
            for game_id, game in self.games.items():
                # Remove games inactive for 1 hour
                if (current_time - game.updated_at.timestamp()) > 3600:
                    to_remove.append(game_id)
            
            for game_id in to_remove:
                del self.games[game_id]

# Singleton instance
game_service = GameService()