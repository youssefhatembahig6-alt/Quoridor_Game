import pygame
from config import (
    BOARD_SIZE, CELL_SIZE, WALL_THICKNESS, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    SIDEBAR_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_RADIUS,
    C_BG, C_BOARD_BG, C_CELL, C_CELL_HOVER, C_GRID, C_VALID_MOVE,
    C_WALL_SLOT, C_WALL_HOVER, C_WALL_P1, C_WALL_P2, C_WALL_PLACED,
    C_P1, C_P2, C_P1_BORDER, C_P2_BORDER,
    C_TEXT, C_TEXT_DIM, C_ACCENT, C_SIDEBAR_BG,
    C_BTN, C_BTN_HOVER, C_BTN_ACTIVE, C_WIN_OVERLAY
)

# ─────────────────────────────────────────────
#  COORDINATE HELPERS
#  These convert between board (row, col) and
#  pixel positions on screen.
# ─────────────────────────────────────────────

def cell_to_pixel(row: int, col: int) -> tuple:
    """Return the top-left pixel corner of a board cell."""
    x = BOARD_OFFSET_X + col * CELL_SIZE
    y = BOARD_OFFSET_Y + row * CELL_SIZE
    return x, y

def cell_center(row: int, col: int) -> tuple:
    """Return the pixel center of a board cell (used for drawing pawns)."""
    x, y = cell_to_pixel(row, col)
    return x + CELL_SIZE // 2, y + CELL_SIZE // 2

def pixel_to_cell(px: int, py: int):
    """
    Convert a raw pixel position to a board (row, col).
    Returns None if the click is outside the board area.
    Used by the input handler to know which cell was clicked.
    """
    col = (px - BOARD_OFFSET_X) // CELL_SIZE
    row = (py - BOARD_OFFSET_Y) // CELL_SIZE
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row, col
    return None

def pixel_to_h_wall(px: int, py: int):
    """
    Detect if the cursor is hovering over a horizontal wall slot.
    Horizontal walls sit BETWEEN rows — in the gap below each row.
    Returns (row, col) of the wall anchor, or None.
    A horizontal wall at (r, c) blocks movement between row r and row r+1
    across columns c and c+1.
    """
    GAP = WALL_THICKNESS * 2   # detection zone width in the gap
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            # The gap runs horizontally below row r
            wx = BOARD_OFFSET_X + c * CELL_SIZE
            wy = BOARD_OFFSET_Y + (r + 1) * CELL_SIZE - GAP // 2
            rect = pygame.Rect(wx, wy, CELL_SIZE * 2, GAP)
            if rect.collidepoint(px, py):
                return r, c
    return None

def pixel_to_v_wall(px: int, py: int):
    """
    Detect if the cursor is hovering over a vertical wall slot.
    Vertical walls sit BETWEEN columns — in the gap to the right of each col.
    Returns (row, col) of the wall anchor, or None.
    A vertical wall at (r, c) blocks movement between col c and col c+1
    across rows r and r+1.
    """
    GAP = WALL_THICKNESS * 2
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            wx = BOARD_OFFSET_X + (c + 1) * CELL_SIZE - GAP // 2
            wy = BOARD_OFFSET_Y + r * CELL_SIZE
            rect = pygame.Rect(wx, wy, GAP, CELL_SIZE * 2)
            if rect.collidepoint(px, py):
                return r, c
    return None


# ─────────────────────────────────────────────
#  RENDERER CLASS
#  One instance lives for the whole game session.
#  Call draw_frame() every tick inside the game loop.
# ─────────────────────────────────────────────

class Renderer:
    def __init__(self, screen: pygame.Surface):
        """
        screen  — the main pygame Surface returned by pygame.display.set_mode()
        We pre-load fonts here once so we're not reloading them every frame.
        """
        self.screen = screen
        pygame.font.init()

        # Font sizes used across the UI
        self.font_large  = pygame.font.SysFont("segoeui", 26, bold=True)
        self.font_medium = pygame.font.SysFont("segoeui", 20)
        self.font_small  = pygame.font.SysFont("segoeui", 16)
        self.font_title  = pygame.font.SysFont("segoeui", 32, bold=True)

        # Sidebar x-start (everything in the sidebar draws from here)
        self.sb_x = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET_X * 2

    # ──────────────────────────────────────────
    #  MASTER DRAW CALL
    #  Call this once per frame from the game loop.
    # ──────────────────────────────────────────

    def draw_frame(self, game, valid_moves: list,
                   hover_cell, hover_wall, wall_horizontal: bool,
                   mode: str):
        """
        game          — the Game object (has .board, .players, .current_turn, .winner)
        valid_moves   — list of (row, col) tuples the current player can move to
        hover_cell    — (row, col) the mouse is over, or None
        hover_wall    — (row, col) wall slot the mouse is over, or None
        wall_horizontal — True = H wall preview, False = V wall preview
        mode          — 'move' or 'wall' (current input mode)
        """
        self.screen.fill(C_BG)             # 1. wipe the whole screen dark
        self._draw_board_bg()              # 2. board background panel
        self._draw_cells(hover_cell, valid_moves, mode)  # 3. cell grid + highlights
        self._draw_walls(game.board)       # 4. placed walls
        self._draw_wall_preview(hover_wall, wall_horizontal, game)  # 5. ghost wall
        self._draw_pawns(game.players)     # 6. player circles on top
        self._draw_sidebar(game, mode)     # 7. sidebar panel
        if game.winner:
            self._draw_win_overlay(game.winner)  # 8. win screen (last, on top)

    # ──────────────────────────────────────────
    #  BOARD BACKGROUND
    #  Draws a rounded rectangle behind the grid
    #  to visually separate it from the dark window.
    # ──────────────────────────────────────────

    def _draw_board_bg(self):
        board_w = BOARD_SIZE * CELL_SIZE
        board_h = BOARD_SIZE * CELL_SIZE
        rect = pygame.Rect(
            BOARD_OFFSET_X - 6,
            BOARD_OFFSET_Y - 6,
            board_w + 12,
            board_h + 12
        )
        pygame.draw.rect(self.screen, C_BOARD_BG, rect, border_radius=8)

    # ──────────────────────────────────────────
    #  CELLS
    #  Draws every square on the 9×9 grid.
    #  - Normal cells get C_CELL color
    #  - Hovered cell gets C_CELL_HOVER (feedback)
    #  - Valid move cells get C_VALID_MOVE (green hint)
    #  Grid lines are drawn on top of cells using
    #  pygame.draw.rect with a border (width=1).
    # ──────────────────────────────────────────

    def _draw_cells(self, hover_cell, valid_moves: list, mode: str):
        valid_set = set(valid_moves)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = cell_to_pixel(r, c)
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

                # Pick the fill color based on state
                if mode == 'move' and (r, c) in valid_set:
                    color = C_VALID_MOVE
                elif hover_cell == (r, c) and mode == 'move':
                    color = C_CELL_HOVER
                else:
                    color = C_CELL

                pygame.draw.rect(self.screen, color, rect)
                # Grid outline
                pygame.draw.rect(self.screen, C_GRID, rect, width=1)

    # ──────────────────────────────────────────
    #  PLACED WALLS
    #  Reads board.h_walls and board.v_walls sets
    #  and draws each as a thick colored rectangle.
    #
    #  Horizontal wall at (r, c):
    #    drawn in the gap between row r and row r+1,
    #    spanning columns c and c+1 (2 cells wide).
    #
    #  Vertical wall at (r, c):
    #    drawn in the gap between col c and col c+1,
    #    spanning rows r and r+1 (2 cells tall).
    #
    #  Wall color tells which player placed it.
    #  (We can't know from the board alone which player
    #   placed each wall, so we use a neutral C_WALL_PLACED
    #   color for all placed walls.)
    # ──────────────────────────────────────────

    def _draw_walls(self, board):
        T = WALL_THICKNESS

        # Horizontal walls
        for (r, c) in board.h_walls:
            x = BOARD_OFFSET_X + c * CELL_SIZE
            y = BOARD_OFFSET_Y + (r + 1) * CELL_SIZE - T // 2
            rect = pygame.Rect(x, y, CELL_SIZE * 2, T)
            pygame.draw.rect(self.screen, C_WALL_PLACED, rect, border_radius=3)

        # Vertical walls
        for (r, c) in board.v_walls:
            x = BOARD_OFFSET_X + (c + 1) * CELL_SIZE - T // 2
            y = BOARD_OFFSET_Y + r * CELL_SIZE
            rect = pygame.Rect(x, y, T, CELL_SIZE * 2)
            pygame.draw.rect(self.screen, C_WALL_PLACED, rect, border_radius=3)

    # ──────────────────────────────────────────
    #  WALL PREVIEW (GHOST)
    #  When the player is in 'wall' mode and hovers
    #  over a slot, show a semi-transparent preview
    #  of where the wall would land.
    #  Uses the current player's color so it feels personal.
    # ──────────────────────────────────────────

    def _draw_wall_preview(self, hover_wall, horizontal: bool, game):
        if hover_wall is None:
            return

        r, c = hover_wall
        T = WALL_THICKNESS
        pid = game.current_turn
        color = C_WALL_P1 if pid == 1 else C_WALL_P2

        # Create a surface with per-pixel alpha so we can do transparency
        ghost = pygame.Surface((CELL_SIZE * 2, T) if horizontal else (T, CELL_SIZE * 2),
                                pygame.SRCALPHA)
        ghost.fill((*color, 160))   # 160/255 opacity = semi-transparent

        if horizontal:
            x = BOARD_OFFSET_X + c * CELL_SIZE
            y = BOARD_OFFSET_Y + (r + 1) * CELL_SIZE - T // 2
        else:
            x = BOARD_OFFSET_X + (c + 1) * CELL_SIZE - T // 2
            y = BOARD_OFFSET_Y + r * CELL_SIZE

        self.screen.blit(ghost, (x, y))

    # ──────────────────────────────────────────
    #  PAWNS
    #  Each player is a filled circle with a
    #  brighter border ring drawn on top.
    #  The border gives a "lifted" 3-D feel.
    # ──────────────────────────────────────────

    def _draw_pawns(self, players):
        for player in players:
            cx, cy = cell_center(player.row, player.col)
            color       = C_P1 if player.pid == 1 else C_P2
            border_color = C_P1_BORDER if player.pid == 1 else C_P2_BORDER

            pygame.draw.circle(self.screen, color, (cx, cy), PLAYER_RADIUS)
            pygame.draw.circle(self.screen, border_color, (cx, cy), PLAYER_RADIUS, width=3)

            # Player number label inside the circle
            label = self.font_medium.render(str(player.pid), True, (255, 255, 255))
            lx = cx - label.get_width() // 2
            ly = cy - label.get_height() // 2
            self.screen.blit(label, (lx, ly))

    # ──────────────────────────────────────────
    #  SIDEBAR
    #  Draws the right-side panel containing:
    #    • Game title
    #    • Whose turn it is (with colored indicator)
    #    • Wall counts for both players
    #    • Current mode badge (MOVE / WALL)
    #    • Keyboard shortcut hints
    # ──────────────────────────────────────────

    def _draw_sidebar(self, game, mode: str):
        # Sidebar background
        sb_rect = pygame.Rect(self.sb_x, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT)
        pygame.draw.rect(self.screen, C_SIDEBAR_BG, sb_rect)
        # Thin separator line between board and sidebar
        pygame.draw.line(self.screen, C_GRID,
                         (self.sb_x, 0), (self.sb_x, WINDOW_HEIGHT), 2)

        sx = self.sb_x + 20    # left padding inside sidebar
        sy = 30                # current y cursor (moves down as we draw)

        # ── Title ──
        title = self.font_title.render("QUORIDOR", True, C_ACCENT)
        self.screen.blit(title, (sx, sy))
        sy += 50

        # ── Divider ──
        pygame.draw.line(self.screen, C_GRID,
                         (sx, sy), (self.sb_x + SIDEBAR_WIDTH - 20, sy), 1)
        sy += 16

        # ── Turn indicator ──
        turn_label = self.font_small.render("CURRENT TURN", True, C_TEXT_DIM)
        self.screen.blit(turn_label, (sx, sy))
        sy += 22

        pid = game.current_turn
        p_color = C_P1 if pid == 1 else C_P2
        pygame.draw.circle(self.screen, p_color, (sx + 12, sy + 12), 10)
        turn_text = self.font_large.render(f"Player {pid}", True, p_color)
        self.screen.blit(turn_text, (sx + 30, sy + 2))
        sy += 40

        # ── Wall counts ──
        sy += 10
        walls_label = self.font_small.render("WALLS REMAINING", True, C_TEXT_DIM)
        self.screen.blit(walls_label, (sx, sy))
        sy += 22

        for player in game.players:
            pc = C_P1 if player.pid == 1 else C_P2
            bar_total = SIDEBAR_WIDTH - 50
            # Background bar
            pygame.draw.rect(self.screen, C_BTN,
                             pygame.Rect(sx, sy, bar_total, 14), border_radius=4)
            # Filled portion proportional to walls left
            from config import WALLS_PER_PLAYER
            filled = int(bar_total * player.walls_left / WALLS_PER_PLAYER)
            if filled > 0:
                pygame.draw.rect(self.screen, pc,
                                 pygame.Rect(sx, sy, filled, 14), border_radius=4)
            # Label
            wtext = self.font_small.render(
                f"P{player.pid}: {player.walls_left} walls", True, C_TEXT)
            self.screen.blit(wtext, (sx, sy + 18))
            sy += 42

        sy += 10
        # ── Mode badge ──
        pygame.draw.line(self.screen, C_GRID,
                         (sx, sy), (self.sb_x + SIDEBAR_WIDTH - 20, sy), 1)
        sy += 14

        mode_label = self.font_small.render("MODE", True, C_TEXT_DIM)
        self.screen.blit(mode_label, (sx, sy))
        sy += 22

        # Two mode buttons: MOVE and WALL
        for m, label in [('move', 'M  MOVE'), ('wall', 'W  WALL')]:
            active = (mode == m)
            btn_color = C_BTN_ACTIVE if active else C_BTN
            btn_rect = pygame.Rect(sx, sy, SIDEBAR_WIDTH - 40, 34)
            pygame.draw.rect(self.screen, btn_color, btn_rect, border_radius=6)
            if active:
                pygame.draw.rect(self.screen, C_ACCENT, btn_rect, width=2, border_radius=6)
            btn_text = self.font_medium.render(label, True, C_ACCENT if active else C_TEXT)
            self.screen.blit(btn_text, (sx + 12, sy + 7))
            sy += 44

        sy += 10
        # ── Keyboard hints ──
        pygame.draw.line(self.screen, C_GRID,
                         (sx, sy), (self.sb_x + SIDEBAR_WIDTH - 20, sy), 1)
        sy += 14

        hints = [
            ("R", "Rotate wall"),
            ("Ctrl+Z", "Undo"),
            ("Ctrl+Y", "Redo"),
            ("F5", "Reset"),
            ("Esc", "Menu"),
        ]
        for key, action in hints:
            key_surf = self.font_small.render(key, True, C_ACCENT)
            act_surf = self.font_small.render(action, True, C_TEXT_DIM)
            self.screen.blit(key_surf, (sx, sy))
            self.screen.blit(act_surf, (sx + 70, sy))
            sy += 20

    # ──────────────────────────────────────────
    #  WIN OVERLAY
    #  Drawn last so it appears above everything.
    #  A semi-transparent black panel covers the
    #  board, with a big announcement centered on it.
    # ──────────────────────────────────────────

    def _draw_win_overlay(self, winner: int):
        # Semi-transparent dark overlay covering the whole window
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))    # black at ~70% opacity
        self.screen.blit(overlay, (0, 0))

        # Centered winner text
        color = C_P1 if winner == 1 else C_P2
        win_text = self.font_title.render(f"Player {winner} Wins!", True, color)
        sub_text  = self.font_medium.render("Press F5 to play again  |  Esc for menu",
                                            True, C_TEXT_DIM)

        cx = WINDOW_WIDTH // 2
        cy = WINDOW_HEIGHT // 2

        self.screen.blit(win_text, (cx - win_text.get_width() // 2, cy - 40))
        self.screen.blit(sub_text, (cx - sub_text.get_width() // 2, cy + 10))