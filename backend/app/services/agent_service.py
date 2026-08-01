from ..game.state import GameState
from ..game.logic import get_valid_moves, apply_move
from ..crew_agents.ludo_crew import decide_ai_move
from .commentary import generate_commentary
import asyncio

async def execute_ai_turn(state: GameState) -> dict:
    """
    Handles an AI player's turn: roll dice, decide move, apply, return commentary.
    Returns dict with move_info, new_state snapshot.
    """
    player = state.current_player()
    from ..game.logic import roll_and_set_dice
    dice = roll_and_set_dice(state)

    # Get valid moves
    valid_moves = get_valid_moves(state)
    if not valid_moves:
        state.next_player()
        return {"dice": dice, "move": None, "commentary": f"{player.name} got {dice} but no moves."}

    # Let AI decide
    decision = await decide_ai_move(state)
    token_id = decision.get("token_id", 0)
    # Find the token in valid moves that matches token_id; if ambiguous, pick first
    chosen = next((m for m in valid_moves if m[0].id == token_id), valid_moves[0])
    token, target = chosen

    move_desc = f"Moved token {token.id} to {target}"
    apply_move(state, token, target)

    # Generate commentary
    context = f"Dice: {dice}, {player.name} ki baari."
    commentary = await generate_commentary(player.name, move_desc, context)

    # Check game over
    if state.game_over:
        commentary += f" 🏆 {state.winner.name} jeet gaya!"

    state.next_player()
    return {
        "dice": dice,
        "token_id": token.id,
        "target": {
            "track_index": target.track_index,
            "color": target.color.name if target.color else None
        },
        "commentary": commentary,
    }