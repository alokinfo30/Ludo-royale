from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional
from .board import Color, Cell

class PlayerType(Enum):
    HUMAN = "human"
    AI = "ai"

@dataclass
class Token:
    id: int  # 0-3
    color: Color
    position: Cell  # Base if not on board
    is_home: bool = False

    def __repr__(self):
        return f"Token({self.color.name}-{self.id}, pos={self.position})"

@dataclass
class Player:
    name: str
    color: Color
    type: PlayerType
    tokens: List[Token] = field(default_factory=list)
    finished: bool = False