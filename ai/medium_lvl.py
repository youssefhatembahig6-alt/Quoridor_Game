"""
easy_lvl.py  —  Easy AI for Quoridor
─────────────────────────────────────
Strategy:
  • Every turn take ONE greedy BFS step toward the goal.
  • With WALL_CHANCE probability, place a random valid wall instead.
  • No lookahead whatsoever — purely reactive.
"""

import random
from utils.pathfinding import bfs_next_step, get_valid_pawn_moves, has_path

WALL_CHANCE = 0.15      # 15 % chance to place a random wall instead of moving
MAX_WALL_TRIES = 20     # attempts before giving up on finding a random wall


class EasyAI:
    def __init__(self, pid: int):
        self.pid = pid
        self.opponent_id = 3 - pid

    # ── public API called by main.py ──────────────────────────────────

    def choose_move(self, game) -> dict:
        """
        Returns one of:
            {"type": "pawn", "row": r, "col": c}
            {"type": "wall", "row": r, "col": c, "horizontal": bool}
        """
        me  = game.players[self.pid - 1]

        # Occasionally drop a random wall
        if me.walls_left > 0 and random.random() < WALL_CHANCE:
            wall = self._random_wall(game)
            if wall:
                return wall

        return self._greedy_pawn_move(game)

    # ── pawn movement ─────────────────────────────────────────────────

    def _greedy_pawn_move(self, game) -> dict:
        me  = game.players[self.pid - 1]
        opp = game.players[self.opponent_id - 1]

        step = bfs_next_step(
            game.board, me.row, me.col, me.goal_row, opp.row, opp.col
        )
        if step:
            return {"type": "pawn", "row": step[0], "col": step[1]}

        # Fallback: any valid move
        valid = get_valid_pawn_moves(game.board, me.row, me.col, opp.row, opp.col)
        if valid:
            r, c = random.choice(valid)
            return {"type": "pawn", "row": r, "col": c}

        # Should never reach here in a legal game state
        return {"type": "pawn", "row": me.row, "col": me.col}

    # ── wall placement ────────────────────────────────────────────────

    def _random_wall(self, game) -> dict | None:
        """Pick a random geometrically valid wall that doesn't trap anyone."""
        board = game.board
        p1, p2 = game.players[0], game.players[1]

        for _ in range(MAX_WALL_TRIES):
            r = random.randint(0, 7)
            c = random.randint(0, 7)
            horizontal = random.choice([True, False])

            if horizontal:
                if not board.can_place_h_wall(r, c):
                    continue
                board.place_h_wall(r, c)
                ok = (has_path(board, p1.row, p1.col, p1.goal_row) and
                      has_path(board, p2.row, p2.col, p2.goal_row))
                board.remove_h_wall(r, c)
            else:
                if not board.can_place_v_wall(r, c):
                    continue
                board.place_v_wall(r, c)
                ok = (has_path(board, p1.row, p1.col, p1.goal_row) and
                      has_path(board, p2.row, p2.col, p2.goal_row))
                board.remove_v_wall(r, c)

            if ok:
                return {"type": "wall", "row": r, "col": c, "horizontal": horizontal}

        return None  # couldn't find a valid random wall in time
