from typing import List, Tuple

from .board import Position, Token
from .state import GameState


def get_valid_moves(state: GameState) -> List[Tuple[Token, Position]]:
    """Return the current valid moves for the active player."""
    if state.dice_value is None:
        return []

    current_player = state.current_turn
    return state.board.get_valid_moves(current_player, state.dice_value)


def apply_move(state: GameState, token: Token, target: Position):
    """Apply a move to the board and update state metadata."""
    if state.dice_value is None:
        raise ValueError("No dice value set")

    color = state.current_turn
    state.board.move_token(token, target, color)


def roll_and_set_dice(state: GameState) -> int:
    """Roll the dice and update the state with the resulting moves."""
    return state.roll_dice()
