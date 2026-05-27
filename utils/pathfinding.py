from collections import deque
from config import BOARD_SIZE


# ─────────────────────────────────────────────
#  has_path
#  BFS check: can player at (start_row, start_col)
#  reach goal_row given current walls?
#  Called on every wall placement to enforce the
#  "no trapping" rule.
# ─────────────────────────────────────────────

def has_path(board, start_row: int, start_col: int, goal_row: int) -> bool:
    visited = set()
    queue   = deque()
    start   = (start_row, start_col)
    queue.append(start)
    visited.add(start)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        r, c = queue.popleft()
        if r == goal_row:
            return True
        for dr, dc in directions:
            nr, nc = r + dr, c + dc
            if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
                continue
            if board.is_blocked(r, c, dr, dc):
                continue
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))
    return False


# ─────────────────────────────────────────────
#  bfs_distance
#  Return the shortest path length (in steps)
#  from (start_row, start_col) to any cell in
#  goal_row, ignoring opponent pawns.
#  Returns float('inf') if no path exists.
#  Used by the AI evaluation and wall-scoring.
# ─────────────────────────────────────────────

def bfs_distance(board, start_row: int, start_col: int, goal_row: int) -> float:
    visited = {(start_row, start_col)}
    queue   = deque([(start_row, start_col, 0)])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        r, c, dist = queue.popleft()
        if r == goal_row:
            return dist
        for dr, dc in directions:
            if board.is_blocked(r, c, dr, dc):
                continue
            nr, nc = r + dr, c + dc
            if (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc, dist + 1))
    return float('inf')


# ─────────────────────────────────────────────
#  bfs_next_step
#  Return the first (row, col) step on the BFS
#  shortest path from start to goal_row.
#  Used by Easy and Medium AI to greedily advance
#  toward the goal each turn.
#  Returns None if no path exists.
# ─────────────────────────────────────────────

def bfs_next_step(board,
                  start_row: int, start_col: int,
                  goal_row: int,
                  opp_r: int = None, opp_c: int = None):
    start  = (start_row, start_col)
    parent = {start: None}
    queue  = deque([start])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    found  = None

    while queue:
        r, c = queue.popleft()
        if r == goal_row:
            found = (r, c)
            break
        for dr, dc in directions:
            if board.is_blocked(r, c, dr, dc):
                continue
            nr, nc = r + dr, c + dc
            if (nr, nc) not in parent:
                parent[(nr, nc)] = (r, c)
                queue.append((nr, nc))

    if found is None:
        return None
    if found == start:
        return start

    # Trace the path back to find the first step after start
    node = found
    while parent[node] != start:
        node = parent[node]
        if node is None:
            return None
    return node


# ─────────────────────────────────────────────
#  get_valid_pawn_moves
#  Returns a list of (row, col) cells the pawn
#  at (r, c) can legally reach this turn.
#  Handles: normal steps, straight jumps over the
#  opponent, and diagonal sidesteps when the jump
#  is blocked by a wall or the board edge.
# ─────────────────────────────────────────────

def get_valid_pawn_moves(board,
                         r: int, c: int,
                         opp_r: int, opp_c: int) -> list:
    moves      = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc

        if board.is_blocked(r, c, dr, dc):
            continue

        # Normal move — destination is empty
        if (nr, nc) != (opp_r, opp_c):
            moves.append((nr, nc))
            continue

        # Destination is the opponent — try straight jump
        jr, jc = nr + dr, nc + dc
        straight_ok = (
            0 <= jr < BOARD_SIZE and
            0 <= jc < BOARD_SIZE and
            not board.is_blocked(nr, nc, dr, dc)
        )

        if straight_ok:
            moves.append((jr, jc))
        else:
            # Straight jump blocked — try diagonal sidesteps
            sidesteps = [(-1, 0), (1, 0)] if dr == 0 else [(0, -1), (0, 1)]
            for sdr, sdc in sidesteps:
                sr, sc = nr + sdr, nc + sdc
                if not (0 <= sr < BOARD_SIZE and 0 <= sc < BOARD_SIZE):
                    continue
                if not board.is_blocked(nr, nc, sdr, sdc):
                    moves.append((sr, sc))

    return moves