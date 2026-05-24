"""
medium_lvl.py  —  Medium AI for Quoridor
─────────────────────────────────────────
Strategy (greedy one-ply evaluation):
  • Option A — Move pawn:  take the BFS-optimal next step toward goal.
  • Option B — Place wall: scan candidate positions near the opponent,
               pick the wall that adds the most BFS steps to the opponent.
  • Choose whichever option yields a higher score.
  • No deep lookahead — smarter than Easy, but still single-move horizon.
"""

import random
from utils.pathfinding import bfs_distance, bfs_next_step, get_valid_pawn_moves, has_path

MIN_WALL_GAIN   = 2    # only place a wall if it costs the opponent ≥ this many extra steps
MAX_CANDIDATES  = 30   # cap on wall positions evaluated per turn


class MediumAI:
    def __init__(self, pid: int):
        self.pid = pid
        self.opponent_id = 3 - pid

    # ── public API ───────────────────────────────────────────────────

    def choose_move(self, game) -> dict:
        me = game.players[self.pid - 1]

        # Always find the best pawn move
        pawn_move  = self._best_pawn_move(game)
        pawn_score = self._pawn_score(game, pawn_move)

        # Evaluate walls only when we have some left
        wall_move, wall_score = None, 0
        if me.walls_left > 0:
            wall_move, wall_score = self._best_wall_move(game)

        if wall_move and wall_score > pawn_score:
            return wall_move
        return pawn_move

    # ── pawn movement ────────────────────────────────────────────────

    def _best_pawn_move(self, game) -> dict:
        me  = game.players[self.pid - 1]
        opp = game.players[self.opponent_id - 1]

        step = bfs_next_step(
            game.board, me.row, me.col, me.goal_row, opp.row, opp.col
        )
        if step:
            return {"type": "pawn", "row": step[0], "col": step[1]}

        valid = get_valid_pawn_moves(game.board, me.row, me.col, opp.row, opp.col)
        if valid:
            r, c = random.choice(valid)
            return {"type": "pawn", "row": r, "col": c}

        return {"type": "pawn", "row": me.row, "col": me.col}

    def _pawn_score(self, game, move: dict) -> float:
        """How many steps closer to goal does this pawn move get us?"""
        me = game.players[self.pid - 1]
        before = bfs_distance(game.board, me.row, me.col, me.goal_row)
        after  = bfs_distance(game.board, move["row"], move["col"], me.goal_row)
        return before - after   # positive = got closer

    # ── wall evaluation ──────────────────────────────────────────────

    def _best_wall_move(self, game) -> tuple:
        board = game.board
        p1, p2 = game.players[0], game.players[1]
        opp = game.players[self.opponent_id - 1]
        opp_dist = bfs_distance(board, opp.row, opp.col, opp.goal_row)

        best_move  = None
        best_gain  = MIN_WALL_GAIN - 1   # must beat this threshold

        for r, c, horizontal in self._candidates(game):
            gain = self._wall_gain(board, r, c, horizontal, p1, p2, opp, opp_dist)
            if gain > best_gain:
                best_gain = gain
                best_move = {"type": "wall", "row": r, "col": c, "horizontal": horizontal}

        return best_move, best_gain

    def _candidates(self, game) -> list:
        """Wall positions near the opponent, capped at MAX_CANDIDATES."""
        opp   = game.players[self.opponent_id - 1]
        board = game.board
        out   = []

        for dr in range(-3, 4):
            for dc in range(-3, 4):
                r, c = opp.row + dr, opp.col + dc
                if 0 <= r <= 7 and 0 <= c <= 7:
                    if board.can_place_h_wall(r, c):
                        out.append((r, c, True))
                    if board.can_place_v_wall(r, c):
                        out.append((r, c, False))

        random.shuffle(out)
        return out[:MAX_CANDIDATES]

    def _wall_gain(self, board, r, c, horizontal, p1, p2, opp, opp_dist) -> float:
        """Extra BFS steps the wall forces on the opponent. -inf if it traps someone."""
        if horizontal:
            if not board.can_place_h_wall(r, c):
                return float('-inf')
            board.place_h_wall(r, c)
        else:
            if not board.can_place_v_wall(r, c):
                return float('-inf')
            board.place_v_wall(r, c)

        if (has_path(board, p1.row, p1.col, p1.goal_row) and
                has_path(board, p2.row, p2.col, p2.goal_row)):
            gain = bfs_distance(board, opp.row, opp.col, opp.goal_row) - opp_dist
        else:
            gain = float('-inf')

        if horizontal:
            board.remove_h_wall(r, c)
        else:
            board.remove_v_wall(r, c)

        return gain
