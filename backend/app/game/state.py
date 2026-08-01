from dataclasses import dataclass, field
from typing import List, Optional, Dict
from enum import Enum
from datetime import datetime
import asyncio
from .constants import Color, TokenState
from .board import LudoBoard, Token, Position
from .rules import GameRules

class GamePhase(Enum):
    WAITING = "waiting"
    ROLLING = "rolling"
    MOVING = "moving"
    FINISHED = "finished"

@dataclass
class PlayerState:
    """State of a player in the game"""
    user_id: Optional[str]
    name: str
    color: Color
    is_ai: bool = False
    is_connected: bool = True
    is_ready: bool = False
    consecutive_sixes: int = 0
    total_moves: int = 0
    total_captures: int = 0
    score: int = 0
    finished: bool = False
    finish_position: Optional[int] = None
    
    def to_dict(self) -> dict:
        return {
            "userId": self.user_id,
            "name": self.name,
            "color": self.color.name,
            "isAI": self.is_ai,
            "isConnected": self.is_connected,
            "isReady": self.is_ready,
            "consecutiveSixes": self.consecutive_sixes,
            "totalMoves": self.total_moves,
            "totalCaptures": self.total_captures,
            "score": self.score,
            "finished": self.finished,
            "finishPosition": self.finish_position
        }

@dataclass
class GameState:
    """Complete game state"""
    game_id: str = ""
    board: LudoBoard = field(default_factory=LudoBoard)
    players: Dict[Color, PlayerState] = field(default_factory=dict)
    current_turn: Color = Color.RED
    phase: GamePhase = GamePhase.WAITING
    dice_value: Optional[int] = None
    valid_moves: List[dict] = field(default_factory=list)
    selected_token: Optional[int] = None
    move_history: List[dict] = field(default_factory=list)
    chat_messages: List[dict] = field(default_factory=list)
    turn_start_time: Optional[datetime] = None
    turn_timeout: int = 30
    winner: Optional[Color] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.game_id:
            self.game_id = str(id(self))

        if isinstance(self.players, list):
            normalized_players = {}
            for player in self.players:
                color = getattr(player, "color", None)
                if color is None:
                    continue
                is_ai = False
                player_type = getattr(player, "type", None)
                if player_type is not None:
                    player_type_value = getattr(player_type, "value", player_type)
                    is_ai = player_type_value == "ai"
                normalized_players[color] = PlayerState(
                    user_id=getattr(player, "user_id", None),
                    name=getattr(player, "name", color.name),
                    color=color,
                    is_ai=is_ai,
                    finished=getattr(player, "finished", False),
                )
            self.players = normalized_players
        elif self.players is None:
            self.players = {}

    def current_player(self) -> Optional[PlayerState]:
        return self.players.get(self.current_turn)

    def next_player(self):
        self._next_turn()
        return self.current_player()

    @property
    def game_over(self) -> bool:
        return self.phase == GamePhase.FINISHED or self.winner is not None
    
    def add_player(self, user_id: Optional[str], name: str, 
                   color: Color, is_ai: bool = False):
        """Add a player to the game"""
        self.players[color] = PlayerState(
            user_id=user_id,
            name=name,
            color=color,
            is_ai=is_ai
        )
    
    def remove_player(self, color: Color):
        """Remove a player and optionally replace with AI"""
        if color in self.players:
            player = self.players[color]
            if not player.is_ai:
                # Convert to AI
                player.is_ai = True
                player.is_connected = False
                player.name = f"AI_{color.name}"
    
    def start_turn(self):
        """Start a new turn"""
        self.phase = GamePhase.ROLLING
        self.dice_value = None
        self.valid_moves = []
        self.selected_token = None
        self.turn_start_time = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def roll_dice(self) -> int:
        """Roll dice for current turn"""
        if self.phase != GamePhase.ROLLING:
            raise ValueError("Not in rolling phase")
        
        self.dice_value = GameRules.roll_dice()
        current_player = self.players[self.current_turn]
        
        # Track consecutive sixes
        if self.dice_value == 6:
            current_player.consecutive_sixes += 1
            if current_player.consecutive_sixes >= 3:
                # Three consecutive sixes - lose turn
                self.dice_value = 0  # Invalid roll
                current_player.consecutive_sixes = 0
                self._next_turn()
                return 0
        else:
            current_player.consecutive_sixes = 0
        
        # Calculate valid moves
        valid_moves = self.board.get_valid_moves(self.current_turn, self.dice_value)
        
        if valid_moves:
            self.phase = GamePhase.MOVING
            self.valid_moves = [
                {
                    "tokenId": token.id,
                    "from": token.position.to_dict(),
                    "to": position.to_dict()
                }
                for token, position in valid_moves
            ]
        else:
            # No valid moves - next turn
            self._next_turn()
        
        self.updated_at = datetime.utcnow()
        return self.dice_value
    
    def make_move(self, token_id: int) -> dict:
        """Execute a move"""
        if self.phase != GamePhase.MOVING:
            raise ValueError("Not in moving phase")
        
        # Find the valid move
        move_data = None
        for move in self.valid_moves:
            if move["tokenId"] == token_id:
                move_data = move
                break
        
        if not move_data:
            raise ValueError("Invalid token selection")
        
        # Get token
        token = self.board.tokens[self.current_turn][token_id]
        target_position = Position.from_dict(move_data["to"])
        
        # Execute move
        captured_color = self.board.move_token(token, target_position, self.current_turn)
        
        # Update player stats
        player = self.players[self.current_turn]
        player.total_moves += 1
        if captured_color:
            player.total_captures += 1
        
        # Record move
        move_record = {
            "moveNumber": len(self.move_history) + 1,
            "player": self.current_turn.name,
            "playerName": player.name,
            "tokenId": token_id,
            "diceValue": self.dice_value,
            "from": move_data["from"],
            "to": move_data["to"],
            "captured": captured_color.name if captured_color else None,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.move_history.append(move_record)
        
        # Check for win
        if self.board.has_won(self.current_turn):
            player.finished = True
            player.finish_position = len([p for p in self.players.values() if p.finished])
            if not self.winner:
                self.winner = self.current_turn
        
        # Check if game is over (all players except one finished)
        unfinished = [p for p in self.players.values() if not p.finished]
        if len(unfinished) <= 1:
            self.phase = GamePhase.FINISHED
            if not self.winner and unfinished:
                self.winner = unfinished[0].color
        
        # Determine if extra turn
        got_capture = captured_color is not None
        landed_on_star = GameRules.is_star_position(target_position)
        gets_extra = GameRules.gets_extra_turn(self.dice_value, got_capture, landed_on_star)
        
        if not gets_extra and self.phase != GamePhase.FINISHED:
            self._next_turn()
        
        self.updated_at = datetime.utcnow()
        
        return {
            "move": move_record,
            "captured": captured_color.name if captured_color else None,
            "extraTurn": gets_extra,
            "gameOver": self.phase == GamePhase.FINISHED,
            "winner": self.winner.name if self.winner else None
        }
    
    def _next_turn(self):
        """Move to next player's turn"""
        if self.phase == GamePhase.FINISHED:
            return
        
        # Find next player
        colors = list(Color)
        current_idx = colors.index(self.current_turn)
        
        for i in range(1, 5):
            next_idx = (current_idx + i) % 4
            next_color = colors[next_idx]
            if next_color in self.players:
                if not self.players[next_color].finished:
                    self.current_turn = next_color
                    self.start_turn()
                    return
        
        # All players finished
        self.phase = GamePhase.FINISHED
    
    def to_dict(self) -> dict:
        """Convert complete game state to dictionary"""
        return {
            "gameId": self.game_id,
            "board": self.board.to_dict(),
            "players": {
                color.name: player.to_dict()
                for color, player in self.players.items()
            },
            "currentTurn": self.current_turn.name,
            "phase": self.phase.value,
            "diceValue": self.dice_value,
            "validMoves": self.valid_moves,
            "selectedToken": self.selected_token,
            "moveHistory": self.move_history[-10:],  # Last 10 moves
            "chatMessages": self.chat_messages[-50:],  # Last 50 messages
            "turnTimeLeft": self._get_time_left(),
            "winner": self.winner.name if self.winner else None,
            "createdAt": self.created_at.isoformat(),
            "updatedAt": self.updated_at.isoformat()
        }
    
    def _get_time_left(self) -> int:
        """Get remaining time for current turn"""
        if not self.turn_start_time:
            return self.turn_timeout
        elapsed = (datetime.utcnow() - self.turn_start_time).total_seconds()
        return max(0, self.turn_timeout - int(elapsed))