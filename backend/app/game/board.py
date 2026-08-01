from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from .constants import (
    Color, CellType, TOTAL_CELLS, HOME_STRETCH_LENGTH,
    START_POSITIONS, HOME_ENTRY_POINTS, SAFE_CELLS, STAR_CELLS,
    get_color_path, TokenState
)
import json

@dataclass
class Position:
    """Represents a position on the Ludo board"""
    type: str  # base, track, home_stretch, home
    index: Optional[int] = None  # track index (0-51) or home stretch index (0-5)
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "index": self.index
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        return cls(
            type=data.get("type", TokenState.IN_BASE),
            index=data.get("index")
        )
    
    def __eq__(self, other):
        if not isinstance(other, Position):
            return False
        return self.type == other.type and self.index == other.index

@dataclass
class Cell(Position):
    """Compatibility wrapper for the older API that expected a Cell-like object."""
    color: Optional[Color] = None

    def __init__(self, track_index: Optional[int] = None, color: Optional[Color] = None, type: Optional[str] = None):
        if type is not None:
            super().__init__(type=type, index=track_index)
        elif track_index is None:
            super().__init__(type=TokenState.IN_BASE, index=None)
        else:
            super().__init__(type=CellType.TRACK, index=track_index)
        self.color = color

    @property
    def track_index(self) -> Optional[int]:
        return self.index

    @track_index.setter
    def track_index(self, value: Optional[int]) -> None:
        self.index = value

    def is_base(self) -> bool:
        return self.type == TokenState.IN_BASE

    def is_home_stretch(self) -> bool:
        return self.type == CellType.HOME_STRETCH

@dataclass
class Token:
    """Represents a game token (goti)"""
    id: int
    color: Color
    position: Position = field(default_factory=lambda: Position(type=TokenState.IN_BASE))
    is_active: bool = False
    steps_moved: int = 0
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "color": self.color.name,
            "position": self.position.to_dict(),
            "is_active": self.is_active,
            "steps_moved": self.steps_moved
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Token':
        return cls(
            id=data["id"],
            color=Color[data["color"]],
            position=Position.from_dict(data["position"]),
            is_active=data.get("is_active", False),
            steps_moved=data.get("steps_moved", 0)
        )

class LudoBoard:
    """Complete Ludo board with all game logic"""
    
    def __init__(self):
        self.tokens: Dict[int, List[Token]] = {}
        self.initialize_board()
    
    def initialize_board(self):
        """Initialize all tokens in their bases"""
        for color in Color:
            self.tokens[color] = [
                Token(id=i, color=color)
                for i in range(4)
            ]
    
    def get_token_position_on_path(self, color: Color, token: Token) -> Optional[int]:
        """Get the absolute position of a token on the color's path"""
        if token.position.type == TokenState.IN_BASE:
            return None
        
        path = get_color_path(color)
        
        if token.position.type in [CellType.TRACK, CellType.SAFE, CellType.STAR]:
            # Find position on main track
            for i, (cell_type, cell_index) in enumerate(path):
                if cell_index == token.position.index:
                    return i
        elif token.position.type == CellType.HOME_STRETCH:
            # Home stretch position
            track_end = TOTAL_CELLS  # position after completing main track
            return track_end + token.position.index
        
        return None
    
    def get_valid_moves(self, color: Color, dice_value: int) -> List[Tuple[Token, Position]]:
        """Get all valid moves for a color given dice value"""
        valid_moves = []
        tokens = self.tokens[color]
        
        for token in tokens:
            moves = self._get_token_moves(token, color, dice_value)
            valid_moves.extend([(token, move) for move in moves])
        
        return valid_moves
    
    def _get_token_moves(self, token: Token, color: Color, dice_value: int) -> List[Position]:
        """Calculate possible moves for a single token"""
        moves = []
        
        # Token in base - needs 6 to come out
        if token.position.type == TokenState.IN_BASE:
            if dice_value == 6:
                start_pos = Position(
                    type=CellType.TRACK,
                    index=START_POSITIONS[color]
                )
                moves.append(start_pos)
            return moves
        
        # Token already finished
        if token.position.type == TokenState.FINISHED:
            return moves
        
        # Calculate new position
        path = get_color_path(color)
        current_path_pos = self.get_token_position_on_path(color, token)
        
        if current_path_pos is None:
            return moves
        
        new_path_pos = current_path_pos + dice_value
        
        # Check if move would overshoot home
        if new_path_pos > len(path) - 1:
            return moves
        
        # Get new position
        if new_path_pos == len(path) - 1:
            # Reached home
            new_position = Position(type=TokenState.FINISHED)
        elif new_path_pos >= TOTAL_CELLS:
            # In home stretch
            home_stretch_index = new_path_pos - TOTAL_CELLS
            new_position = Position(
                type=CellType.HOME_STRETCH,
                index=home_stretch_index
            )
        else:
            # On main track
            cell_type, cell_index = path[new_path_pos]
            new_position = Position(
                type=cell_type,
                index=cell_index
            )
        
        # Check if position is occupied by own token
        if self._is_own_token_at_position(color, new_position):
            return moves
        
        moves.append(new_position)
        return moves
    
    def move_token(self, token: Token, new_position: Position, color: Color) -> Optional[Color]:
        """Move token and handle captures. Returns captured color if any."""
        old_position = token.position
        token.position = new_position
        token.steps_moved += 1
        
        # Check for capture
        if new_position.type in [CellType.TRACK, CellType.STAR] and \
           new_position.index not in SAFE_CELLS:
            captured_color = self._check_capture(new_position, color)
            if captured_color is not None:
                return captured_color
        
        return None
    
    def _check_capture(self, position: Position, moving_color: Color) -> Optional[Color]:
        """Check if any opponent token is at this position and capture it"""
        for color in Color:
            if color == moving_color:
                continue
            for token in self.tokens[color]:
                if token.position == position:
                    # Send back to base
                    token.position = Position(type=TokenState.IN_BASE)
                    token.is_active = False
                    token.steps_moved = 0
                    return color
        return None
    
    def _is_own_token_at_position(self, color: Color, position: Position) -> bool:
        """Check if player's own token is at the position"""
        for token in self.tokens[color]:
            if token.position == position:
                return True
        return False
    
    def can_any_token_move(self, color: Color, dice_value: int) -> bool:
        """Check if any token can move with the given dice value"""
        return len(self.get_valid_moves(color, dice_value)) > 0
    
    def has_won(self, color: Color) -> bool:
        """Check if all tokens of a color have reached home"""
        return all(
            token.position.type == TokenState.FINISHED
            for token in self.tokens[color]
        )
    
    def to_dict(self) -> dict:
        """Convert board state to dictionary"""
        return {
            "tokens": {
                color.name: [token.to_dict() for token in tokens]
                for color, tokens in self.tokens.items()
            }
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'LudoBoard':
        """Create board from dictionary"""
        board = cls()
        if "tokens" in data:
            for color_name, tokens_data in data["tokens"].items():
                color = Color[color_name]
                board.tokens[color] = [
                    Token.from_dict(token_data)
                    for token_data in tokens_data
                ]
        return board