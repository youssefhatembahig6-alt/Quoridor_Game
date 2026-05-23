import pygame
from gui.renderer import pixel_to_cell, pixel_to_h_wall, pixel_to_v_wall


# ─────────────────────────────────────────────
#  INPUT HANDLER
#  Sits between raw pygame events and the game logic.
#  It never modifies game state itself — it reads
#  events and calls the appropriate method on `rules`.
#
#  It also tracks UI-only state that the renderer
#  needs but the game engine doesn't care about:
#    • current mode  ('move' or 'wall')
#    • wall orientation (horizontal or vertical)
#    • what the mouse is hovering over
# ─────────────────────────────────────────────

class InputHandler:

    def __init__(self, rules, on_reset, on_menu):
        """
        rules     — the Rules object (has try_move_pawn, try_place_wall, undo, redo)
        on_reset  — a zero-arg callback called when F5 is pressed  (resets the game)
        on_menu   — a zero-arg callback called when Escape is pressed (goes to menu)

        Storing callbacks instead of the full game object keeps this class
        loosely coupled — it doesn't need to know how reset or menu work.
        """
        self.rules       = rules
        self.on_reset    = on_reset
        self.on_menu     = on_menu

        # ── UI-only state ──────────────────────────────────────────────
        # mode controls what a mouse click does
        self.mode             = 'move'       # 'move' | 'wall'
        self.wall_horizontal  = True         # True = H wall, False = V wall

        # These are updated every frame from mouse position
        # and read by the Renderer to draw highlights/ghost
        self.hover_cell  = None   # (row, col) or None
        self.hover_wall  = None   # (row, col) or None

    # ──────────────────────────────────────────
    #  MAIN ENTRY POINT
    #  Call this every frame from the game loop,
    #  passing the full list of pygame events.
    # ──────────────────────────────────────────

    def handle(self, events: list, game):
        """
        events — pygame.event.get() from the game loop
        game   — the live Game object (read-only here, mutations go through rules)
        """
        self._update_hover(game)          # always refresh hover state from mouse pos

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                self._handle_click(event, game)

            elif event.type == pygame.KEYDOWN:
                self._handle_key(event, game)

    # ──────────────────────────────────────────
    #  HOVER DETECTION
    #  Called every frame regardless of clicks.
    #  Updates self.hover_cell and self.hover_wall
    #  so the renderer can draw highlights and the
    #  ghost wall preview in real time.
    # ──────────────────────────────────────────

    def _update_hover(self, game):
        """Read current mouse position and update hover targets."""
        if game.winner:
            # No hover feedback when game is over
            self.hover_cell = None
            self.hover_wall = None
            return

        mx, my = pygame.mouse.get_pos()

        if self.mode == 'move':
            # In move mode only track cell hover, not walls
            self.hover_cell = pixel_to_cell(mx, my)
            self.hover_wall = None

        else:  # wall mode
            # In wall mode only track wall slot hover, not cells
            self.hover_cell = None
            if self.wall_horizontal:
                self.hover_wall = pixel_to_h_wall(mx, my)
            else:
                self.hover_wall = pixel_to_v_wall(mx, my)

    # ──────────────────────────────────────────
    #  MOUSE CLICKS
    #  Left click behaves differently depending
    #  on current mode:
    #    move mode  → try to move pawn to clicked cell
    #    wall mode  → try to place wall at hovered slot
    #  Right click → rotate wall orientation (shortcut)
    # ──────────────────────────────────────────

    def _handle_click(self, event: pygame.event.Event, game):
        if game.winner:
            return   # ignore all clicks when game is over

        if event.button == 1:    # left click
            self._handle_left_click(game)

        elif event.button == 3:  # right click
            self._rotate_wall()

    def _handle_left_click(self, game):
        mx, my = pygame.mouse.get_pos()

        if self.mode == 'move':
            # ── Move pawn ──────────────────────────────────────────────
            # Convert pixel → cell, then ask rules if that move is legal.
            # rules.try_move_pawn() returns True on success, False if invalid.
            cell = pixel_to_cell(mx, my)
            if cell is not None:
                self.rules.try_move_pawn(cell[0], cell[1])

        else:   # wall mode
            # ── Place wall ─────────────────────────────────────────────
            # Use whichever wall slot is currently hovered (already computed
            # in _update_hover), then call rules to validate and place.
            if self.hover_wall is not None:
                r, c = self.hover_wall
                self.rules.try_place_wall(r, c, self.wall_horizontal)

    # ──────────────────────────────────────────
    #  KEYBOARD INPUT
    #  All keyboard shortcuts are handled here.
    #  Shortcuts are context-free (work any time)
    #  except undo/redo which check game state.
    # ──────────────────────────────────────────

    def _handle_key(self, event: pygame.event.Event, game):
        key  = event.key
        mods = pygame.key.get_mods()   # lets us detect Ctrl, Shift, Alt

        # ── Mode switching ─────────────────────────────────────────────
        # M and W just flip self.mode; no game state changes.
        if key == pygame.K_m:
            self.mode = 'move'

        elif key == pygame.K_w:
            self.mode = 'wall'

        # ── Rotate wall orientation ────────────────────────────────────
        # R key toggles between horizontal and vertical wall preview.
        elif key == pygame.K_r:
            self._rotate_wall()

        # ── Undo (Ctrl + Z) ────────────────────────────────────────────
        # mods & KMOD_CTRL is True when either Ctrl key is held.
        # rules.undo() pops the last snapshot and restores game state.
        elif key == pygame.K_z and (mods & pygame.KMOD_CTRL):
            self.rules.undo()

        # ── Redo (Ctrl + Y) ────────────────────────────────────────────
        elif key == pygame.K_y and (mods & pygame.KMOD_CTRL):
            self.rules.redo()

        # ── Reset game (F5) ────────────────────────────────────────────
        # Calls the on_reset callback provided at construction.
        # Also resets local UI state so mode/hover don't carry over.
        elif key == pygame.K_F5:
            self._reset_ui_state()
            self.on_reset()

        # ── Back to menu (Escape) ──────────────────────────────────────
        elif key == pygame.K_ESCAPE:
            self._reset_ui_state()
            self.on_menu()

    # ──────────────────────────────────────────
    #  HELPERS
    # ──────────────────────────────────────────

    def _rotate_wall(self):
        """
        Toggle wall orientation between horizontal and vertical.
        Called by both R key and right mouse click.
        Also clears hover_wall so the ghost doesn't flicker on the
        wrong orientation for one frame.
        """
        self.wall_horizontal = not self.wall_horizontal
        self.hover_wall = None    # force re-detection next frame

    def _reset_ui_state(self):
        """
        Snap all UI-only state back to defaults.
        Called on reset and menu exit so the new game
        always starts in move mode with no stale hover.
        """
        self.mode            = 'move'
        self.wall_horizontal = True
        self.hover_cell      = None
        self.hover_wall      = None

    # ──────────────────────────────────────────
    #  PROPERTIES
    #  The renderer reads these each frame to know
    #  what to highlight and what ghost to draw.
    #  Exposing them as properties keeps the data
    #  flow one-directional: renderer reads, never writes.
    # ──────────────────────────────────────────

    @property
    def current_mode(self) -> str:
        return self.mode

    @property
    def is_wall_horizontal(self) -> bool:
        return self.wall_horizontal