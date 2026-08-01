from enum import IntEnum
from typing import Dict, List, Tuple

class Color(IntEnum):
    RED = 0
    GREEN = 1
    YELLOW = 2
    BLUE = 3

class CellType(str):
    BASE = "base"
    TRACK = "track"
    HOME_STRETCH = "home_stretch"
    HOME = "home"
    SAFE = "safe"
    STAR = "star"

# Board configuration
TOTAL_CELLS = 52
HOME_STRETCH_LENGTH = 6
TOKENS_PER_PLAYER = 4
DICE_FACES = 6
MAX_CONSECUTIVE_SIXES = 3

# Starting positions on the main track
START_POSITIONS: Dict[Color, int] = {
    Color.RED: 0,
    Color.GREEN: 13,
    Color.YELLOW: 26,
    Color.BLUE: 39,
}

# Entry point to home stretch (cell before entering)
HOME_ENTRY_POINTS: Dict[Color, int] = {
    Color.RED: 50,
    Color.GREEN: 11,
    Color.YELLOW: 24,
    Color.BLUE: 37,
}

# Safe cells (star positions) on main track
SAFE_CELLS: List[int] = [0, 8, 13, 21, 26, 34, 39, 47]

# Star positions (give extra turn)
STAR_CELLS: List[int] = [8, 21, 34, 47]

# Home stretch positions relative to color
HOME_STRETCH_START: Dict[Color, int] = {
    Color.RED: 1,
    Color.GREEN: 14,
    Color.YELLOW: 27,
    Color.BLUE: 40,
}

# Complete path mapping for each color
# Format: [(cell_type, cell_index), ...]
def get_color_path(color: Color) -> List[Tuple[str, int]]:
    """Returns complete path for a color including main track and home stretch"""
    start = START_POSITIONS[color]
    path = []
    
    # Main track (52 cells)
    for i in range(TOTAL_CELLS):
        cell_index = (start + i) % TOTAL_CELLS
        cell_type = CellType.TRACK
        if cell_index in SAFE_CELLS:
            cell_type = CellType.SAFE
        if cell_index in STAR_CELLS:
            cell_type = CellType.STAR
        path.append((cell_type, cell_index))
    
    # Home stretch
    for i in range(HOME_STRETCH_LENGTH):
        path.append((CellType.HOME_STRETCH, i))
    
    # Home
    path.append((CellType.HOME, -1))
    
    return path

# Token states
class TokenState:
    IN_BASE = "base"
    ON_TRACK = "track"
    IN_HOME_STRETCH = "home_stretch"
    FINISHED = "finished"