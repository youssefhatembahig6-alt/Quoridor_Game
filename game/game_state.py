# ─────────────────────────────────────────────
#  GameState
#  A frozen snapshot of the entire game at one
#  moment in time. Created by rules.py before
#  every move and pushed onto the History stack
#  so that undo/redo can restore any past state.
#
#  Key design rule: GameState never holds live
#  references to the game's objects — it always
#  stores COPIES, so later mutations to the board
#  or players don't corrupt the saved snapshot.
# ─────────────────────────────────────────────

class GameState:
    def __init__(self, players, board, current_turn: int, move_number: int):
        """
        players      — list of Player objects (we deep-copy each one)
        board        — Board object            (we deep-copy it)
        current_turn — 1 or 2, whose turn it is at this moment
        move_number  — integer counter of total moves made so far
        """
        # Deep-copy both players so future position/wall changes
        # don't affect this snapshot.
        self.players      = [p.copy() for p in players]

        # Deep-copy the board so future wall additions/removals
        # don't affect this snapshot.
        self.board        = board.copy()

        # Primitive values are already immutable — no copy needed.
        self.current_turn = current_turn
        self.move_number  = move_number

    # ──────────────────────────────────────────
    #  restore_to
    #  Pushes this snapshot's data back into the
    #  live Game object. Called by rules.undo()
    #  and rules.redo() after popping from History.
    #
    #  We write each field individually (rather than
    #  replacing `game` itself) because the Rules,
    #  InputHandler, and Renderer all hold a reference
    #  to the same Game object — swapping it out would
    #  break those references silently.
    # ──────────────────────────────────────────

    def restore_to(self, game):
        """
        game — the live Game object whose state we are restoring.
        """
        # Restore each player's position and wall count from our copies.
        for i, saved_player in enumerate(self.players):
            game.players[i].row        = saved_player.row
            game.players[i].col        = saved_player.col
            game.players[i].walls_left = saved_player.walls_left
            # goal_row and pid never change during a game — no need to restore.

        # Restore the board's wall sets from our copies.
        game.board.h_walls = set(self.board.h_walls)
        game.board.v_walls = set(self.board.v_walls)

        # Restore turn and move counter.
        game.current_turn = self.current_turn
        game.move_number  = self.move_number

        # Clear winner so the game is playable again after an undo
        # that reverses the winning move.
        game.winner = None
        for player in game.players:
            if player.has_won():
                game.winner = player.pid
                break

    # ──────────────────────────────────────────
    #  __repr__
    #  Useful for debugging: print(snapshot) shows
    #  a compact summary without needing a debugger.
    # ──────────────────────────────────────────

    def __repr__(self):
        p_info = ", ".join(
            f"P{p.pid}@({p.row},{p.col}) w={p.walls_left}"
            for p in self.players
        )
        return (
            f"GameState(turn={self.current_turn}, "
            f"move={self.move_number}, [{p_info}], "
            f"h_walls={len(self.board.h_walls)}, "
            f"v_walls={len(self.board.v_walls)})"
        )