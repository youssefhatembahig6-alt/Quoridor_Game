from config import BOARD_SIZE

class Board:


    def __init__(self):
        self.h_walls: set = set()   # horizontal walls placed
        self.v_walls: set = set()   # vertical walls placed

    def copy(self):
        b = Board()
        b.h_walls = set(self.h_walls)
        b.v_walls = set(self.v_walls)
        return b

    # ------------------------------------------------------------------
    # Wall placement helpers
    # ------------------------------------------------------------------

    def can_place_h_wall(self, r: int, c: int) -> bool:
        """Check if a horizontal wall at (r,c) is geometrically valid (no overlap/cross)."""
        if not (0 <= r < BOARD_SIZE - 1 and 0 <= c < BOARD_SIZE - 1):
            return False
        # No duplicate
        if (r, c) in self.h_walls:
            return False
        # No adjacent horizontal wall sharing a cell
        if (r, c - 1) in self.h_walls or (r, c + 1) in self.h_walls:
            return False
        # No crossing vertical wall
        if (r, c) in self.v_walls:
            return False
        return True

    def can_place_v_wall(self, r: int, c: int) -> bool:
        """Check if a vertical wall at (r,c) is geometrically valid."""
        if not (0 <= r < BOARD_SIZE - 1 and 0 <= c < BOARD_SIZE - 1):
            return False
        if (r, c) in self.v_walls:
            return False
        if (r - 1, c) in self.v_walls or (r + 1, c) in self.v_walls:
            return False
        if (r, c) in self.h_walls:
            return False
        return True

    def place_h_wall(self, r: int, c: int):
        self.h_walls.add((r, c))

    def place_v_wall(self, r: int, c: int):
        self.v_walls.add((r, c))

    def remove_h_wall(self, r: int, c: int):
        self.h_walls.discard((r, c))

    def remove_v_wall(self, r: int, c: int):
        self.v_walls.discard((r, c))

    # ------------------------------------------------------------------
    # Movement blocking
    # ------------------------------------------------------------------

    def is_blocked(self, r: int, c: int, dr: int, dc: int) -> bool:
        """Return True if moving from (r,c) by (dr,dc) is blocked by a wall."""
        nr, nc = r + dr, c + dc
        if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
            return True  # Board edge

        if dr == 1:   # Moving south: blocked by h_wall at (r, c) or (r, c-1)
            return (r, c) in self.h_walls or (r, c - 1) in self.h_walls
        if dr == -1:  # Moving north: blocked by h_wall at (r-1, c) or (r-1, c-1)
            return (r - 1, c) in self.h_walls or (r - 1, c - 1) in self.h_walls
        if dc == 1:   # Moving east: blocked by v_wall at (r, c) or (r-1, c)
            return (r, c) in self.v_walls or (r - 1, c) in self.v_walls
        if dc == -1:  # Moving west: blocked by v_wall at (r, c-1) or (r-1, c-1)
            return (r, c - 1) in self.v_walls or (r - 1, c - 1) in self.v_walls
        return False
