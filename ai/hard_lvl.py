"""
hard_lvl.py  —  Hard AI for Quoridor
──────────────────────────────────────
Strategy: Minimax with Alpha-Beta Pruning

  • Thinks SEARCH_DEPTH half-moves ahead (AI turn + opponent turn = 2 plies).
  • At each node generates: all valid pawn moves + top-N impactful wall moves.
  • Evaluation function:
        score = opponent_path_length − ai_path_length
    (positive → AI is ahead; negative → opponent is ahead)
  • Alpha-Beta pruning eliminates branches that can't change the outcome,
    keeping response time under ~1 second at depth 4.
"""

import random
from utils.pathfinding import bfs_distance, get_valid_pawn_moves, has_path

SEARCH_DEPTH   = 4    # plies to look ahead (increase for harder, costs time)
MAX_WALL_MOVES = 8    # wall candidates evaluated at each minimax node
INF            = float('inf')


class HardAI:
    def __init__(self, pid: int):
        self.pid = pid
        self.opponent_id = 3 - pid

    # ── public API ───────────────────────────────────────────────────

    def choose_move(self, game) -> dict:
        best_move  = None
        best_score = -INF
        alpha, beta = -INF, INF

        for move in self._generate_moves(game, self.pid):
            child = self._apply_move(game, move, self.pid)
            if child is None:
                continue
            score = self._minimax(child, SEARCH_DEPTH - 1, alpha, beta, maximising=False)
            if score > best_score:
                best_score = score
                best_move  = move
            alpha = max(alpha, best_score)

        # Absolute fallback (should never trigger in legal game)
        if best_move is None:
            me  = game.players[self.pid - 1]
            opp = game.players[self.opponent_id - 1]
            valid = get_valid_pawn_moves(game.board, me.row, me.col, opp.row, opp.col)
            if valid:
                r, c = random.choice(valid)
                best_move = {"type": "pawn", "row": r, "col": c}

        return best_move

    # ── minimax ──────────────────────────────────────────────────────

    def _minimax(self, game, depth: int, alpha: float, beta: float,
                 maximising: bool) -> float:
        # Terminal: someone has won
        for p in game.players:
            if p.has_won():
                return INF if p.pid == self.pid else -INF

        # Leaf node: evaluate statically
        if depth == 0:
            return self._evaluate(game)

        current_pid = self.pid if maximising else self.opponent_id

        if maximising:
            best = -INF
            for move in self._generate_moves(game, current_pid):
                child = self._apply_move(game, move, current_pid)
                if child is None:
                    continue
                score = self._minimax(child, depth - 1, alpha, beta, False)
                best  = max(best, score)
                alpha = max(alpha, best)
                if beta <= alpha:
                    break   # β cut-off
            return best if best != -INF else self._evaluate(game)

        else:
            best = INF
            for move in self._generate_moves(game, current_pid):
                child = self._apply_move(game, move, current_pid)
                if child is None:
                    continue
                score = self._minimax(child, depth - 1, alpha, beta, True)
                best  = min(best, score)
                beta  = min(beta, best)
                if beta <= alpha:
                    break   # α cut-off
            return best if best != INF else self._evaluate(game)

    # ── evaluation function ──────────────────────────────────────────

    def _evaluate(self, game) -> float:
        me  = game.players[self.pid - 1]
        opp = game.players[self.opponent_id - 1]
        my_dist  = bfs_distance(game.board, me.row,  me.col,  me.goal_row)
        opp_dist = bfs_distance(game.board, opp.row, opp.col, opp.goal_row)
        if my_dist  == INF: return -INF
        if opp_dist == INF: return  INF
        # Main term: opponent further = better for us
        # Small wall bonus: having more walls is a mild advantage
        return (opp_dist - my_dist) + (me.walls_left - opp.walls_left) * 0.5

    # ── move generation ──────────────────────────────────────────────

    def _generate_moves(self, game, pid: int) -> list:
        player = game.players[pid - 1]
        opp    = game.players[3 - pid - 1]
        moves  = []

        # Pawn moves — sorted by resulting BFS distance (best first for pruning)
        valid_pawns = get_valid_pawn_moves(
            game.board, player.row, player.col, opp.row, opp.col
        )
        pawn_moves = [{"type": "pawn", "row": r, "col": c} for r, c in valid_pawns]
        pawn_moves.sort(
            key=lambda m: bfs_distance(game.board, m["row"], m["col"], player.goal_row)
        )
        moves.extend(pawn_moves)

        # Wall moves — top N by impact on opponent
        if player.walls_left > 0:
            moves.extend(self._top_wall_moves(game, pid))

        return moves

    def _top_wall_moves(self, game, pid: int) -> list:
        board  = game.board
        opp    = game.players[3 - pid - 1]
        p1, p2 = game.players[0], game.players[1]
        opp_dist = bfs_distance(board, opp.row, opp.col, opp.goal_row)

        scored = []
        for dr in range(-2, 3):
            for dc in range(-2, 3):
                r, c = opp.row + dr, opp.col + dc
                if not (0 <= r <= 7 and 0 <= c <= 7):
                    continue
                for horizontal in (True, False):
                    gain = self._wall_gain(board, r, c, horizontal, p1, p2, opp, opp_dist)
                    if gain > 0:
                        scored.append((gain, r, c, horizontal))

        scored.sort(reverse=True, key=lambda x: x[0])
        return [
            {"type": "wall", "row": r, "col": c, "horizontal": h}
            for _, r, c, h in scored[:MAX_WALL_MOVES]
        ]

    def _wall_gain(self, board, r, c, horizontal, p1, p2, opp, opp_dist) -> float:
        if horizontal:
            if not board.can_place_h_wall(r, c): return 0
            board.place_h_wall(r, c)
        else:
            if not board.can_place_v_wall(r, c): return 0
            board.place_v_wall(r, c)

        if (has_path(board, p1.row, p1.col, p1.goal_row) and
                has_path(board, p2.row, p2.col, p2.goal_row)):
            gain = bfs_distance(board, opp.row, opp.col, opp.goal_row) - opp_dist
        else:
            gain = 0

        if horizontal: board.remove_h_wall(r, c)
        else:          board.remove_v_wall(r, c)
        return gain

    # ── state cloning ────────────────────────────────────────────────

    def _apply_move(self, game, move: dict, pid: int):
        """Return a cloned game state with the move applied, or None if invalid."""
        clone = self._clone(game)
        player = clone.players[pid - 1]
        opp    = clone.players[3 - pid - 1]
        board  = clone.board

        if move["type"] == "pawn":
            valid = get_valid_pawn_moves(board, player.row, player.col, opp.row, opp.col)
            if (move["row"], move["col"]) not in valid:
                return None
            player.row, player.col = move["row"], move["col"]
            clone.current_turn = 3 - pid

        elif move["type"] == "wall":
            if player.walls_left <= 0:
                return None
            r, c, h = move["row"], move["col"], move["horizontal"]
            if h:
                if not board.can_place_h_wall(r, c): return None
                board.place_h_wall(r, c)
            else:
                if not board.can_place_v_wall(r, c): return None
                board.place_v_wall(r, c)
            p1, p2 = clone.players[0], clone.players[1]
            if not (has_path(board, p1.row, p1.col, p1.goal_row) and
                    has_path(board, p2.row, p2.col, p2.goal_row)):
                return None
            player.walls_left -= 1
            clone.current_turn = 3 - pid

        return clone

    def _clone(self, game):
        """Lightweight clone: only what the search tree needs."""
        class _G: pass
        g = _G()
        g.board        = game.board.copy()
        g.players      = [p.copy() for p in game.players]
        g.current_turn = game.current_turn
        g.winner       = getattr(game, "winner", None)
        return g
