import pygame
from gui.renderer import pixel_to_cell, pixel_to_h_wall, pixel_to_v_wall


class InputHandler:

    def __init__(self, rules, renderer, on_reset, on_menu):
        self.rules    = rules
        self.renderer = renderer          # used to read sidebar button rects
        self.on_reset = on_reset
        self.on_menu  = on_menu

        self.mode            = 'move'
        self.wall_horizontal = True
        self.hover_cell      = None
        self.hover_wall      = None
        self.hover_sidebar_btn = None     # which sidebar btn the mouse is over

    # ── Main entry ───────────────────────────────────────────────────

    def handle(self, events, game, allow_board_click=True):
        """
        allow_board_click — False during AI turns so the human can't
                            move, but keyboard shortcuts still fire.
        """
        self._update_hover(game, allow_board_click)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event, game, allow_board_click)
            elif event.type == pygame.KEYDOWN:
                self._handle_key(event, game)

    # ── Hover ────────────────────────────────────────────────────────

    def _update_hover(self, game, allow_board_click):
        mx, my = pygame.mouse.get_pos()

        # Sidebar button hover (always active — helps visual feedback)
        self.hover_sidebar_btn = None
        for name, rect in self.renderer.sidebar_rects.items():
            if rect.collidepoint(mx, my):
                self.hover_sidebar_btn = name
                break

        if not allow_board_click or game.winner:
            self.hover_cell = None
            self.hover_wall = None
            return

        if self.mode == 'move':
            self.hover_cell = pixel_to_cell(mx, my)
            self.hover_wall = None
        else:
            self.hover_cell = None
            self.hover_wall = (pixel_to_h_wall(mx, my)
                               if self.wall_horizontal
                               else pixel_to_v_wall(mx, my))

    # ── Mouse clicks ─────────────────────────────────────────────────

    def _handle_click(self, event, game, allow_board_click):
        if event.button == 3:
            self._rotate_wall(); return

        if event.button != 1:
            return

        mx, my = pygame.mouse.get_pos()

        # ── Sidebar buttons (always clickable) ──────────────────────
        for name, rect in self.renderer.sidebar_rects.items():
            if rect.collidepoint(mx, my):
                if name == 'move':
                    self.mode = 'move'
                elif name == 'wall':
                    self.mode = 'wall'
                elif name == 'rotate':
                    self._rotate_wall()
                elif name == 'reset':
                    self._reset_ui_state(); self.on_reset()
                elif name == 'menu':
                    self._reset_ui_state(); self.on_menu()
                return

        # ── Board clicks (blocked during AI turn or after win) ──────
        if not allow_board_click or game.winner:
            return

        if self.mode == 'move':
            cell = pixel_to_cell(mx, my)
            if cell:
                self.rules.try_move_pawn(cell[0], cell[1])
        else:
            if self.hover_wall:
                r, c = self.hover_wall
                self.rules.try_place_wall(r, c, self.wall_horizontal)

    # ── Keyboard ─────────────────────────────────────────────────────

    def _handle_key(self, event, game):
        key  = event.key
        mods = pygame.key.get_mods()

        if key == pygame.K_m:
            self.mode = 'move'
        elif key == pygame.K_w:
            self.mode = 'wall'
        elif key == pygame.K_r:
            self._rotate_wall()
        elif key == pygame.K_z and (mods & pygame.KMOD_CTRL):
            self.rules.undo()
        elif key == pygame.K_y and (mods & pygame.KMOD_CTRL):
            self.rules.redo()
        elif key == pygame.K_F5:
            self._reset_ui_state(); self.on_reset()
        elif key == pygame.K_ESCAPE:
            self._reset_ui_state(); self.on_menu()

    # ── Helpers ──────────────────────────────────────────────────────

    def _rotate_wall(self):
        self.wall_horizontal = not self.wall_horizontal
        self.hover_wall = None

    def _reset_ui_state(self):
        self.mode            = 'move'
        self.wall_horizontal = True
        self.hover_cell      = None
        self.hover_wall      = None
        self.hover_sidebar_btn = None

    @property
    def current_mode(self):       return self.mode
    @property
    def is_wall_horizontal(self): return self.wall_horizontal