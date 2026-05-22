from utils.pathfinding import has_path, get_valid_pawn_moves
from game.game_state import GameState

class Rules:
    """Validates and applies moves; interfaces with History."""

    def __init__(self, game, history):
        self.game = game
        self.history = history

    # ------------------------------------------------------------------
    # Snapshot helpers
    # ------------------------------------------------------------------

    def _snapshot(self):
        g = self.game
        return GameState(g.players, g.board, g.current_turn, g.move_number)

    # ------------------------------------------------------------------
    # Move pawn
    # ------------------------------------------------------------------

    def valid_pawn_moves(self, pid: int = None):
        g = self.game
        if pid is None:
            pid = g.current_turn
        mover = g.players[pid - 1]
        other = g.players[2 - pid]  # pid 1 -> index 1, pid 2 -> index 0
        return get_valid_pawn_moves(g.board, mover.row, mover.col, other.row, other.col)

    def try_move_pawn(self, r: int, c: int) -> bool:
        g = self.game
        if g.winner:
            return False
        valid = self.valid_pawn_moves()
        if (r, c) not in valid:
            return False

        self.history.push(self._snapshot())
        mover = g.players[g.current_turn - 1]
        mover.row, mover.col = r, c
        g.move_number += 1
        if mover.has_won():
            g.winner = g.current_turn
        else:
            g.current_turn = 3 - g.current_turn  # toggle 1<->2
        return True

    # ------------------------------------------------------------------
    # Place wall
    # ------------------------------------------------------------------

    def try_place_wall(self, r: int, c: int, horizontal: bool) -> bool:
        g = self.game
        if g.winner:
            return False
        player = g.players[g.current_turn - 1]
        if player.walls_left <= 0:
            return False

        board = g.board
        if horizontal:
            if not board.can_place_h_wall(r, c):
                return False
            board.place_h_wall(r, c)
        else:
            if not board.can_place_v_wall(r, c):
                return False
            board.place_v_wall(r, c)

        # Check both players still have a path
        p1, p2 = g.players[0], g.players[1]
        if not has_path(board, p1.row, p1.col, p1.goal_row) or \
           not has_path(board, p2.row, p2.col, p2.goal_row):
            # Revert
            if horizontal:
                board.remove_h_wall(r, c)
            else:
                board.remove_v_wall(r, c)
            return False

        self.history.push(self._snapshot())
        player.walls_left -= 1
        g.move_number += 1
        g.current_turn = 3 - g.current_turn
        return True

    # ------------------------------------------------------------------
    # Undo / Redo
    # ------------------------------------------------------------------

    def undo(self) -> bool:
        snap = self.history.undo()
        if snap is None:
            return False
        # Push current state to redo (history.undo already did that internally)
        snap.restore_to(self.game)
        return True

    def redo(self) -> bool:
        snap = self.history.redo()
        if snap is None:
            return False
        snap.restore_to(self.game)
        return True
