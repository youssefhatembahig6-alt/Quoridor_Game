"""
game/__init__.py  —  Game
─────────────────────────
Top-level container for all mutable game state.
Holds the Board, both Players, turn tracker,
move counter, and winner flag.

Rules, AI, and the Renderer never store game data
themselves — they all read and write through this
single object, so there is exactly one source of
truth at any time.
"""

# Use relative imports (.board / .player) so Python
# doesn't try to re-enter this package while it is
# still being initialized — that would cause the
# "partially initialized module" circular-import error.
from .board  import Board
from .player import Player


class Game:
    def __init__(self):
        self.board        = Board()
        self.players      = [Player(1), Player(2)]
        self.current_turn = 1    # pid of the player whose turn it is
        self.winner       = None # pid of the winner, or None
        self.move_number  = 0    # total half-moves made so far

    # ── Convenience accessors ─────────────────

    @property
    def current_player(self) -> Player:
        return self.players[self.current_turn - 1]

    @property
    def other_player(self) -> Player:
        return self.players[2 - self.current_turn]   # 1→index1, 2→index0

    # ── Full reset ────────────────────────────

    def reset(self):
        """Wipe all state back to a fresh start — called by F5 / new game."""
        self.board        = Board()
        self.players      = [Player(1), Player(2)]
        self.current_turn = 1
        self.winner       = None
        self.move_number  = 0

    def __repr__(self):
        return (f"Game(turn={self.current_turn}, move={self.move_number}, "
                f"winner={self.winner}, "
                f"players={self.players})")