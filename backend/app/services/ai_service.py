from typing import Optional, Dict, List
import random
from ..game.state import GameState, GamePhase
from ..game.constants import Color, SAFE_CELLS, STAR_CELLS
from ..game.board import Position, Token
from ..game.rules import GameRules
from ..ai.openrouter_client import OpenRouterClient

class AIService:
    """AI service for computer players"""
    
    def __init__(self):
        self.ai_client = OpenRouterClient()
        self.ai_personalities = {
            "aggressive": {
                "name_prefix": "Aggressive",
                "strategy": self._aggressive_strategy,
                "description": "Prioritizes capturing opponents"
            },
            "defensive": {
                "name_prefix": "Safe",
                "strategy": self._defensive_strategy,
                "description": "Prioritizes safety"
            },
            "balanced": {
                "name_prefix": "Smart",
                "strategy": self._balanced_strategy,
                "description": "Balanced approach"
            },
            "speedy": {
                "name_prefix": "Speed",
                "strategy": self._speedy_strategy,
                "description": "Focuses on reaching home quickly"
            }
        }
    
    def get_ai_name(self, personality: str, color: Color) -> str:
        """Generate AI player name"""
        prefix = self.ai_personalities.get(personality, {}).get("name_prefix", "AI")
        return f"{prefix}_{color.name}"
    
    async def decide_move(self, game: GameState) -> Optional[int]:
        """Decide which token to move"""
        if game.phase != GamePhase.MOVING or not game.valid_moves:
            return None
        
        current_player = game.players[game.current_turn]
        
        # Determine AI personality based on name
        personality = "balanced"
        for p_type, p_data in self.ai_personalities.items():
            if p_data["name_prefix"].lower() in current_player.name.lower():
                personality = p_type
                break
        
        # Get strategy function
        strategy = self.ai_personalities[personality]["strategy"]
        
        # Use AI for complex decisions, fallback to strategy
        try:
            # Try AI decision first
            ai_decision = await self._get_ai_decision(game, personality)
            if ai_decision is not None:
                return ai_decision
        except Exception:
            pass
        
        # Fallback to rule-based strategy
        return strategy(game)
    
    async def _get_ai_decision(self, game: GameState, personality: str) -> Optional[int]:
        """Get AI decision from OpenRouter"""
        if not game.valid_moves:
            return None
        
        # Prepare game context
        context = self._prepare_game_context(game)
        
        # Get decision from AI
        prompt = f"""
        You are playing Ludo as the {personality} player ({game.current_turn.name}).
        
        Game context:
        {context}
        
        Valid moves:
        {self._format_moves(game.valid_moves)}
        
        Choose the best token to move (0-3). Consider:
        - Capturing opponents when possible
        - Reaching safe positions
        - Advancing tokens toward home
        - Blocking opponents
        
        Respond with just the token number (0-3).
        """
        
        response = await self.ai_client.get_completion(prompt)
        
        try:
            token_id = int(response.strip())
            if 0 <= token_id <= 3:
                # Verify it's a valid move
                if any(move["tokenId"] == token_id for move in game.valid_moves):
                    return token_id
        except (ValueError, IndexError):
            pass
        
        return None
    
    def _aggressive_strategy(self, game: GameState) -> Optional[int]:
        """Aggressive strategy - prioritize captures"""
        moves = game.valid_moves
        
        # Look for captures first
        for move in moves:
            to_pos = Position.from_dict(move["to"])
            if GameRules.check_capture(game.board, game.current_turn, to_pos):
                return move["tokenId"]
        
        # Move token closest to home
        return self._move_closest_to_home(game)
    
    def _defensive_strategy(self, game: GameState) -> Optional[int]:
        """Defensive strategy - prioritize safety"""
        moves = game.valid_moves
        
        # Prefer safe positions
        for move in moves:
            to_pos = Position.from_dict(move["to"])
            if GameRules.is_safe_position(to_pos):
                return move["tokenId"]
        
        # Move token furthest from danger
        return self._move_safest_token(game)
    
    def _balanced_strategy(self, game: GameState) -> Optional[int]:
        """Balanced strategy"""
        moves = game.valid_moves
        
        # 40% chance aggressive, 60% defensive
        if random.random() < 0.4:
            return self._aggressive_strategy(game)
        return self._defensive_strategy(game)
    
    def _speedy_strategy(self, game: GameState) -> Optional[int]:
        """Speed strategy - focus on reaching home"""
        return self._move_closest_to_home(game)
    
    def _move_closest_to_home(self, game: GameState) -> Optional[int]:
        """Move token that is closest to home"""
        if not game.valid_moves:
            return None
        
        best_move = None
        max_progress = -1
        
        for move in game.valid_moves:
            token = game.board.tokens[game.current_turn][move["tokenId"]]
            if token.steps_moved > max_progress:
                max_progress = token.steps_moved
                best_move = move["tokenId"]
        
        return best_move if best_move is not None else game.valid_moves[0]["tokenId"]
    
    def _move_safest_token(self, game: GameState) -> Optional[int]:
        """Move token in safest position"""
        if not game.valid_moves:
            return None
        
        # Move token that is in most danger
        for move in game.valid_moves:
            from_pos = Position.from_dict(move["from"])
            if from_pos.type == "track" and from_pos.index not in SAFE_CELLS:
                return move["tokenId"]
        
        return game.valid_moves[0]["tokenId"]
    
    def _prepare_game_context(self, game: GameState) -> str:
        """Prepare game context for AI"""
        context = []
        context.append(f"Current turn: {game.current_turn.name}")
        context.append(f"Dice value: {game.dice_value}")
        context.append(f"Phase: {game.phase.value}")
        
        for color, player in game.players.items():
            tokens_status = []
            for token in game.board.tokens[color]:
                tokens_status.append(f"Token{token.id}: {token.position.type}")
            context.append(f"{player.name}: {', '.join(tokens_status)}")
        
        return "\n".join(context)
    
    def _format_moves(self, valid_moves: List[dict]) -> str:
        """Format valid moves for AI"""
        moves_str = []
        for move in valid_moves:
            moves_str.append(f"Token {move['tokenId']}: {move['from']['type']} -> {move['to']['type']}")
        return "\n".join(moves_str)