from collections import deque
from config import BOARD_SIZE


# ─────────────────────────────────────────────
#  has_path
#  Uses BFS (Breadth-First Search) to check
#  whether a player at (start_row, start_col)
#  can reach any cell in goal_row, given the
#  current wall layout on the board.
#
#  Called by rules.py every time a wall is placed
#  to ensure neither player is completely trapped.
#
#  Returns True  → at least one path exists (wall is legal)
#  Returns False → player is trapped       (wall must be rejected)
# ─────────────────────────────────────────────

def has_path(board, start_row: int, start_col: int, goal_row: int) -> bool:
    """
    BFS from (start_row, start_col) checking every orthogonal
    neighbour that isn't blocked by a wall or the board edge.
    We do NOT handle pawn jumping here — that is only relevant
    during pawn movement, not legality of wall placement.
    """
    visited = set()
    queue   = deque()

    start = (start_row, start_col)
    queue.append(start)
    visited.add(start)

    # The four orthogonal directions: (delta_row, delta_col)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    while queue:
        r, c = queue.popleft()

        # Reached the goal row — a path exists
        if r == goal_row:
            return True

        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # Skip out-of-bounds neighbours
            if not (0 <= nr < BOARD_SIZE and 0 <= nc < BOARD_SIZE):
                continue

            # Skip if a wall blocks this step
            if board.is_blocked(r, c, dr, dc):
                continue

            if (nr, nc) not in visited:
                visited.add((nr, nc))
                queue.append((nr, nc))

    # Exhausted all reachable cells without hitting goal_row
    return False


# ─────────────────────────────────────────────
#  get_valid_pawn_moves
#  Returns a list of (row, col) cells the current
#  player's pawn is legally allowed to move to.
#
#  Quoridor movement rules implemented here:
#    1. Move one step orthogonally if not blocked.
#    2. If the destination is occupied by the opponent,
#       try to JUMP straight over them (if not blocked).
#    3. If the straight jump is blocked by a wall (or
#       the board edge), allow DIAGONAL moves around
#       the opponent instead.
#
#  Called by rules.py on every turn to build the set
#  of valid destinations for highlighting and validation.
# ─────────────────────────────────────────────

def get_valid_pawn_moves(board,
                         r: int, c: int,
                         opp_r: int, opp_c: int) -> list:
    """
    board         — Board object (used for is_blocked)
    r, c          — current player's position
    opp_r, opp_c  — opponent's position
    """
    moves = []
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dr, dc in directions:
        nr, nc = r + dr, c + dc

        # ── Step blocked by wall or board edge ──────────────────────
        if board.is_blocked(r, c, dr, dc):
            continue

        # ── Destination is empty → normal move ──────────────────────
        if (nr, nc) != (opp_r, opp_c):
            moves.append((nr, nc))
            continue

        # ── Destination is the opponent's cell ──────────────────────
        # Try straight jump first: one more step in the same direction.
        jr, jc = nr + dr, nc + dc

        straight_jump_ok = (
            0 <= jr < BOARD_SIZE and           # inside the board
            0 <= jc < BOARD_SIZE and
            not board.is_blocked(nr, nc, dr, dc)  # no wall behind opponent
        )

        if straight_jump_ok:
            moves.append((jr, jc))
        else:
            # Straight jump blocked → try the two diagonal sidesteps.
            # Sidestep directions are perpendicular to the original move.
            if dr == 0:
                # Moving horizontally → sidesteps are up and down
                sidesteps = [(-1, 0), (1, 0)]
            else:
                # Moving vertically → sidesteps are left and right
                sidesteps = [(0, -1), (0, 1)]

            for sdr, sdc in sidesteps:
                # The sidestep goes from the opponent's cell sideways.
                sr, sc = nr + sdr, nc + sdc

                if not (0 <= sr < BOARD_SIZE and 0 <= sc < BOARD_SIZE):
                    continue   # sidestep goes off the board

                # Must not be blocked between opponent cell and sidestep cell
                if not board.is_blocked(nr, nc, sdr, sdc):
                    moves.append((sr, sc))

    return moves