from typing import List, Optional, Tuple
from .constants import (
    Color, CellType, SAFE_CELLS, STAR_CELLS,
    MAX_CONSECUTIVE_SIXES, START_POSITIONS, TokenState
)
from .board import LudoBoard, Token, Position
import random

class GameRules:
    """Complete Ludo game rules implementation"""
    
    @staticmethod
    def roll_dice() -> int:
        """Roll a single dice"""
        return random.randint(1, 6)
    
    @staticmethod
    def is_six(dice_value: int) -> bool:
        """Check if dice value is 6"""
        return dice_value == 6
    
    @staticmethod
    def gets_extra_turn(dice_value: int, got_capture: bool, landed_on_star: bool) -> bool:
        """Check if player gets an extra turn"""
        # Get extra turn on 6, capture, or landing on star
        return dice_value == 6 or got_capture or landed_on_star
    
    @staticmethod
    def validate_move(board: LudoBoard, color: Color, token: Token, 
                     target_position: Position, dice_value: int) -> Tuple[bool, str]:
        """Validate a move according to Ludo rules"""
        # Check if it's the correct player's turn (handled externally)
        
        # Check if token belongs to the player
        if token.color != color:
            return False, "Token doesn't belong to player"
        
        # Get valid moves
        valid_moves = board.get_valid_moves(color, dice_value)
        valid_positions = [move for _, move in valid_moves]
        
        # Check if target position is in valid moves
        if target_position not in valid_positions:
            return False, "Invalid move"
        
        # Check if token can move to that position
        token_valid_moves = [move for t, move in valid_moves if t.id == token.id]
        if target_position not in token_valid_moves:
            return False, "Token cannot move to that position"
        
        return True, "Valid move"
    
    @staticmethod
    def check_capture(board: LudoBoard, color: Color, position: Position) -> Optional[Color]:
        """Check if moving to position captures an opponent's token"""
        if position.type not in [CellType.TRACK, CellType.STAR]:
            return None
        
        if position.index in SAFE_CELLS:
            return None
        
        for opp_color in Color:
            if opp_color == color:
                continue
            for token in board.tokens[opp_color]:
                if token.position == position:
                    return opp_color
        
        return None
    
    @staticmethod
    def is_safe_position(position: Position) -> bool:
        """Check if position is safe from capture"""
        if position.type in [CellType.HOME_STRETCH, TokenState.FINISHED]:
            return True
        if position.type == CellType.SAFE:
            return True
        return False
    
    @staticmethod
    def is_star_position(position: Position) -> bool:
        """Check if position is a star (gives extra turn)"""
        if position.type == CellType.STAR:
            return True
        return position.index in STAR_CELLS
    
    @staticmethod
    def get_possible_captures(board: LudoBoard, color: Color, 
                             dice_value: int) -> List[Tuple[Token, Position, Color]]:
        """Get all moves that result in captures"""
        captures = []
        valid_moves = board.get_valid_moves(color, dice_value)
        
        for token, position in valid_moves:
            captured = GameRules.check_capture(board, color, position)
            if captured:
                captures.append((token, position, captured))
        
        return captures
    
    @staticmethod
    def calculate_score(color: Color, board: LudoBoard, 
                       moves_count: int, captures: int) -> int:
        """Calculate score for a player"""
        score = 0
        tokens = board.tokens[color]
        
        # Points for token progress
        for token in tokens:
            if token.position.type == TokenState.IN_BASE:
                score += 0
            elif token.position.type == TokenState.FINISHED:
                score += 100
            elif token.position.type == CellType.HOME_STRETCH:
                score += 75 + token.position.index * 10
            else:
                # On track - calculate distance from start
                distance = (token.position.index - START_POSITIONS[color]) % 52
                score += min(distance, 50)
        
        # Bonus for captures
        score += captures * 50
        
        # Bonus for finishing first
        if board.has_won(color):
            score += 200
        
        return score