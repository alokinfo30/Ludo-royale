from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from ..database import Base

class GameStatus(str, enum.Enum):
    WAITING = "waiting"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"

class PlayerColor(str, enum.Enum):
    RED = "red"
    GREEN = "green"
    YELLOW = "yellow"
    BLUE = "blue"

class PlayerType(str, enum.Enum):
    HUMAN = "human"
    AI = "ai"

class Game(Base):
    __tablename__ = "games"
    
    id = Column(Integer, primary_key=True, index=True)
    game_code = Column(String(6), unique=True, index=True)
    status = Column(SQLEnum(GameStatus), default=GameStatus.WAITING)
    board_state = Column(JSON, default={})
    current_turn = Column(Integer, default=0)
    dice_value = Column(Integer, nullable=True)
    winner_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    players = relationship("Player", back_populates="game", cascade="all, delete-orphan")
    moves = relationship("Move", back_populates="game", cascade="all, delete-orphan")

class Player(Base):
    __tablename__ = "players"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    user_id = Column(String(100), nullable=True)  # null for AI
    name = Column(String(50))
    color = Column(SQLEnum(PlayerColor))
    type = Column(SQLEnum(PlayerType), default=PlayerType.HUMAN)
    position = Column(Integer)  # player order 0-3
    is_ready = Column(Boolean, default=False)
    is_connected = Column(Boolean, default=False)
    tokens_state = Column(JSON, default=[])
    score = Column(Integer, default=0)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    game = relationship("Game", back_populates="players")

class Move(Base):
    __tablename__ = "moves"
    
    id = Column(Integer, primary_key=True, index=True)
    game_id = Column(Integer, ForeignKey("games.id"))
    player_id = Column(Integer, ForeignKey("players.id"))
    move_number = Column(Integer)
    dice_roll = Column(Integer)
    token_id = Column(Integer)
    from_position = Column(JSON)
    to_position = Column(JSON)
    captured_token = Column(Boolean, default=False)
    captured_player_id = Column(Integer, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    game = relationship("Game", back_populates="moves")