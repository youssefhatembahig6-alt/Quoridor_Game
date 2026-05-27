import pygame
from config import (
    BOARD_SIZE, CELL_SIZE, WALL_THICKNESS, BOARD_OFFSET_X, BOARD_OFFSET_Y,
    SIDEBAR_WIDTH, WINDOW_WIDTH, WINDOW_HEIGHT, PLAYER_RADIUS,
    C_BG, C_BOARD_BG, C_CELL, C_CELL_HOVER, C_GRID, C_VALID_MOVE,
    C_WALL_SLOT, C_WALL_HOVER, C_WALL_P1, C_WALL_P2, C_WALL_PLACED,
    C_P1, C_P2, C_P1_BORDER, C_P2_BORDER,
    C_TEXT, C_TEXT_DIM, C_ACCENT, C_SIDEBAR_BG,
    C_BTN, C_BTN_HOVER, C_BTN_ACTIVE, C_WIN_OVERLAY,
    WALLS_PER_PLAYER,
)

# ── Coordinate helpers ────────────────────────────────────────────────────────

def cell_to_pixel(row, col):
    return BOARD_OFFSET_X + col * CELL_SIZE, BOARD_OFFSET_Y + row * CELL_SIZE

def cell_center(row, col):
    x, y = cell_to_pixel(row, col)
    return x + CELL_SIZE // 2, y + CELL_SIZE // 2

def pixel_to_cell(px, py):
    col = (px - BOARD_OFFSET_X) // CELL_SIZE
    row = (py - BOARD_OFFSET_Y) // CELL_SIZE
    if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:
        return row, col
    return None

def pixel_to_h_wall(px, py):
    GAP = WALL_THICKNESS * 2
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            rect = pygame.Rect(
                BOARD_OFFSET_X + c * CELL_SIZE,
                BOARD_OFFSET_Y + (r+1) * CELL_SIZE - GAP // 2,
                CELL_SIZE * 2, GAP)
            if rect.collidepoint(px, py):
                return r, c
    return None

def pixel_to_v_wall(px, py):
    GAP = WALL_THICKNESS * 2
    for r in range(BOARD_SIZE - 1):
        for c in range(BOARD_SIZE - 1):
            rect = pygame.Rect(
                BOARD_OFFSET_X + (c+1) * CELL_SIZE - GAP // 2,
                BOARD_OFFSET_Y + r * CELL_SIZE,
                GAP, CELL_SIZE * 2)
            if rect.collidepoint(px, py):
                return r, c
    return None


# ── Renderer ──────────────────────────────────────────────────────────────────

class Renderer:
    def __init__(self, screen):
        self.screen = screen
        pygame.font.init()
        self.font_large  = pygame.font.SysFont("segoeui", 26, bold=True)
        self.font_medium = pygame.font.SysFont("segoeui", 20)
        self.font_small  = pygame.font.SysFont("segoeui", 15)
        self.font_title  = pygame.font.SysFont("segoeui", 32, bold=True)
        self.sb_x = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET_X * 2

        # Populated each frame by _draw_sidebar — InputHandler reads these
        self.sidebar_rects = {}

    # ── Master draw call ──────────────────────────────────────────────

    def draw_frame(self, game, valid_moves, hover_cell, hover_wall,
                   wall_horizontal, mode, hover_btn=None):
        self.screen.fill(C_BG)
        self._draw_board_bg()
        self._draw_cells(hover_cell, valid_moves, mode)
        if mode == 'wall' and not game.winner:
            self._draw_wall_slots(game.board, wall_horizontal)
        self._draw_walls(game.board)
        self._draw_wall_preview(hover_wall, wall_horizontal, game)
        self._draw_pawns(game.players)
        self._draw_sidebar(game, mode, hover_btn)
        if game.winner:
            self._draw_win_overlay(game.winner)

    # ── Board background ──────────────────────────────────────────────

    def _draw_board_bg(self):
        bw = BOARD_SIZE * CELL_SIZE
        rect = pygame.Rect(BOARD_OFFSET_X-6, BOARD_OFFSET_Y-6, bw+12, bw+12)
        pygame.draw.rect(self.screen, C_BOARD_BG, rect, border_radius=8)
        pygame.draw.rect(self.screen, C_GRID, rect, width=2, border_radius=8)

    # ── Cells ─────────────────────────────────────────────────────────

    def _draw_cells(self, hover_cell, valid_moves, mode):
        valid_set = set(valid_moves)
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = cell_to_pixel(r, c)
                rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
                if mode == 'move' and (r, c) in valid_set:
                    color = C_VALID_MOVE
                elif hover_cell == (r, c) and mode == 'move':
                    color = C_CELL_HOVER
                else:
                    color = C_CELL
                pygame.draw.rect(self.screen, color, rect)
                pygame.draw.rect(self.screen, C_GRID, rect, width=1)

    # ── Wall slot indicators ──────────────────────────────────────────

    def _draw_wall_slots(self, board, horizontal):
        """Subtle dashed lines showing available wall positions."""
        T = 3
        for r in range(BOARD_SIZE - 1):
            for c in range(BOARD_SIZE - 1):
                if horizontal:
                    if board.can_place_h_wall(r, c):
                        cy = BOARD_OFFSET_Y + (r+1) * CELL_SIZE
                        for seg in range(2):
                            sx = BOARD_OFFSET_X + (c+seg)*CELL_SIZE + 6
                            pygame.draw.rect(self.screen, C_WALL_SLOT,
                                pygame.Rect(sx, cy - T//2, CELL_SIZE-12, T))
                else:
                    if board.can_place_v_wall(r, c):
                        cx = BOARD_OFFSET_X + (c+1) * CELL_SIZE
                        for seg in range(2):
                            sy_seg = BOARD_OFFSET_Y + (r+seg)*CELL_SIZE + 6
                            pygame.draw.rect(self.screen, C_WALL_SLOT,
                                pygame.Rect(cx - T//2, sy_seg, T, CELL_SIZE-12))

    # ── Placed walls ──────────────────────────────────────────────────

    def _draw_walls(self, board):
        T = WALL_THICKNESS
        for (r, c) in board.h_walls:
            pygame.draw.rect(self.screen, C_WALL_PLACED,
                pygame.Rect(BOARD_OFFSET_X + c*CELL_SIZE,
                            BOARD_OFFSET_Y + (r+1)*CELL_SIZE - T//2,
                            CELL_SIZE*2, T), border_radius=3)
        for (r, c) in board.v_walls:
            pygame.draw.rect(self.screen, C_WALL_PLACED,
                pygame.Rect(BOARD_OFFSET_X + (c+1)*CELL_SIZE - T//2,
                            BOARD_OFFSET_Y + r*CELL_SIZE,
                            T, CELL_SIZE*2), border_radius=3)

    # ── Wall ghost preview ────────────────────────────────────────────

    def _draw_wall_preview(self, hover_wall, horizontal, game):
        if hover_wall is None:
            return
        r, c  = hover_wall
        T     = WALL_THICKNESS + 2
        color = C_WALL_P1 if game.current_turn == 1 else C_WALL_P2

        if horizontal:
            w, h = CELL_SIZE*2, T
            x = BOARD_OFFSET_X + c*CELL_SIZE
            y = BOARD_OFFSET_Y + (r+1)*CELL_SIZE - T//2
        else:
            w, h = T, CELL_SIZE*2
            x = BOARD_OFFSET_X + (c+1)*CELL_SIZE - T//2
            y = BOARD_OFFSET_Y + r*CELL_SIZE

        ghost = pygame.Surface((w, h), pygame.SRCALPHA)
        ghost.fill((*color, 180))
        self.screen.blit(ghost, (x, y))
        pygame.draw.rect(self.screen, color,
                         pygame.Rect(x, y, w, h), width=1, border_radius=2)

    # ── Pawns ─────────────────────────────────────────────────────────

    def _draw_pawns(self, players):
        for p in players:
            cx, cy = cell_center(p.row, p.col)
            col    = C_P1 if p.pid == 1 else C_P2
            bord   = C_P1_BORDER if p.pid == 1 else C_P2_BORDER
            pygame.draw.circle(self.screen, col,  (cx, cy), PLAYER_RADIUS)
            pygame.draw.circle(self.screen, bord, (cx, cy), PLAYER_RADIUS, width=3)
            lbl = self.font_medium.render(str(p.pid), True, (255,255,255))
            self.screen.blit(lbl, (cx - lbl.get_width()//2, cy - lbl.get_height()//2))

    # ── Sidebar ───────────────────────────────────────────────────────

    def _draw_sidebar(self, game, mode, hover_btn):
        """
        Draws sidebar and populates self.sidebar_rects so InputHandler
        can detect clicks without duplicating layout math.
        """
        self.sidebar_rects = {}   # reset every frame

        pygame.draw.rect(self.screen, C_SIDEBAR_BG,
                         pygame.Rect(self.sb_x, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
        pygame.draw.line(self.screen, C_GRID,
                         (self.sb_x, 0), (self.sb_x, WINDOW_HEIGHT), 2)

        sx = self.sb_x + 16
        sy = 28
        W  = SIDEBAR_WIDTH - 32   # usable button width

        # ── Title ──
        title = self.font_title.render("QUORIDOR", True, C_ACCENT)
        self.screen.blit(title, (sx, sy)); sy += 48

        self._divider(sx, sy); sy += 14

        # ── Current turn ──
        self._small_label("CURRENT TURN", sx, sy); sy += 20
        pid    = game.current_turn
        pcol   = C_P1 if pid == 1 else C_P2
        pygame.draw.circle(self.screen, pcol, (sx+12, sy+12), 10)
        t = self.font_large.render(f"Player {pid}", True, pcol)
        self.screen.blit(t, (sx+28, sy+2)); sy += 38

        self._divider(sx, sy); sy += 14

        # ── Wall counts ──
        self._small_label("WALLS REMAINING", sx, sy); sy += 20
        for p in game.players:
            pc = C_P1 if p.pid == 1 else C_P2
            bar_w = W
            pygame.draw.rect(self.screen, C_BTN,
                             pygame.Rect(sx, sy, bar_w, 12), border_radius=4)
            filled = int(bar_w * p.walls_left / WALLS_PER_PLAYER)
            if filled > 0:
                pygame.draw.rect(self.screen, pc,
                                 pygame.Rect(sx, sy, filled, 12), border_radius=4)
            wt = self.font_small.render(
                f"P{p.pid}: {p.walls_left} / {WALLS_PER_PLAYER} walls", True, C_TEXT)
            self.screen.blit(wt, (sx, sy+15)); sy += 36

        self._divider(sx, sy); sy += 14

        # ── Mode buttons ──
        self._small_label("MODE", sx, sy); sy += 20

        for m, label in [('move', 'M   Move pawn'), ('wall', 'W   Place wall')]:
            active  = (mode == m)
            hovered = (hover_btn == m)
            self._btn(sx, sy, W, 36, label, active, hovered)
            self.sidebar_rects[m] = pygame.Rect(sx, sy, W, 36)
            sy += 44

        # ── Rotate button (only meaningful in wall mode) ──
        rot_active  = False
        rot_hovered = (hover_btn == 'rotate')
        rot_label   = "R   Rotate wall  (horizontal)" if mode == 'wall' and True else "R   Rotate wall  (vertical)"
        # Just show current orientation
        if mode == 'wall':
            self._btn(sx, sy, W, 36, "R   Rotate wall", rot_active, rot_hovered,
                      dim=(mode != 'wall'))
            self.sidebar_rects['rotate'] = pygame.Rect(sx, sy, W, 36)
        sy += 44

        self._divider(sx, sy); sy += 14

        # ── Action buttons ──
        self._small_label("ACTIONS", sx, sy); sy += 20

        for name, label, key_hint in [
            ('reset', 'F5   New game',   None),
            ('menu',  'Esc  Main menu',  None),
        ]:
            hovered = (hover_btn == name)
            self._btn(sx, sy, W, 32, label, False, hovered)
            self.sidebar_rects[name] = pygame.Rect(sx, sy, W, 32)
            sy += 40

        self._divider(sx, sy); sy += 14

        # ── Keyboard shortcuts reference ──
        self._small_label("SHORTCUTS", sx, sy); sy += 20
        for key, action in [("Ctrl+Z", "Undo"), ("Ctrl+Y", "Redo")]:
            k = self.font_small.render(key,    True, C_ACCENT)
            a = self.font_small.render(action, True, C_TEXT_DIM)
            self.screen.blit(k, (sx, sy))
            self.screen.blit(a, (sx + 72, sy))
            sy += 20

    def _divider(self, sx, sy):
        pygame.draw.line(self.screen, C_GRID,
                         (sx, sy), (self.sb_x + SIDEBAR_WIDTH - 16, sy), 1)

    def _small_label(self, text, sx, sy):
        s = self.font_small.render(text, True, C_TEXT_DIM)
        self.screen.blit(s, (sx, sy))

    def _btn(self, sx, sy, w, h, label, active, hovered, dim=False):
        if active:
            bg, text_col, border = C_BTN_ACTIVE, (255,255,255), C_ACCENT
        elif hovered:
            bg, text_col, border = C_BTN_HOVER, C_TEXT, C_GRID
        elif dim:
            bg, text_col, border = C_BG, C_TEXT_DIM, C_GRID
        else:
            bg, text_col, border = C_BTN, C_TEXT, C_GRID

        rect = pygame.Rect(sx, sy, w, h)
        pygame.draw.rect(self.screen, bg,     rect, border_radius=6)
        pygame.draw.rect(self.screen, border, rect, width=1, border_radius=6)
        s = self.font_small.render(label, True, text_col)
        self.screen.blit(s, (sx + 10, sy + h//2 - s.get_height()//2))

    # ── Win overlay ───────────────────────────────────────────────────

    def _draw_win_overlay(self, winner):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        overlay.fill((242, 238, 229, 210))
        self.screen.blit(overlay, (0, 0))

        color    = C_P1 if winner == 1 else C_P2
        win_text = self.font_title.render(f"Player {winner} Wins!", True, color)
        sub_text = self.font_medium.render(
            "F5 — play again     Esc — main menu", True, C_TEXT_DIM)

        cx = WINDOW_WIDTH  // 2
        cy = WINDOW_HEIGHT // 2
        self.screen.blit(win_text, (cx - win_text.get_width()//2, cy - 40))
        self.screen.blit(sub_text, (cx - sub_text.get_width()//2, cy + 14))