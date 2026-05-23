import pygame
from config import WINDOW_WIDTH, WINDOW_HEIGHT, FPS
from game.board import Board
from game.player import Player
from gui.renderer import Renderer
from gui.input_handler import InputHandler

# ── Mock game ──────────────────────────────────────────
class MockGame:
    def __init__(self):
        self.board = Board()
        self.players = [Player(1), Player(2)]
        self.current_turn = 1
        self.winner = None
        self.board.place_h_wall(3, 3)
        self.board.place_v_wall(5, 5)

# ── Mock rules (stubs so InputHandler doesn't crash) ───
class MockRules:
    def try_move_pawn(self, r, c):
        print(f"[MOVE] → ({r}, {c})")

    def try_place_wall(self, r, c, horizontal):
        orient = "H" if horizontal else "V"
        print(f"[WALL] {orient} → ({r}, {c})")

    def undo(self):
        print("[UNDO]")

    def redo(self):
        print("[REDO]")

# ── Setup ──────────────────────────────────────────────
pygame.init()
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("GUI Test")
clock = pygame.time.Clock()

game     = MockGame()
renderer = Renderer(screen)
handler  = InputHandler(
    rules    = MockRules(),
    on_reset = lambda: print("[RESET]"),
    on_menu  = lambda: print("[MENU]")
)

# ── Game loop ──────────────────────────────────────────
running = True
while running:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            running = False

    handler.handle(events, game)

    renderer.draw_frame(
        game             = game,
        valid_moves      = [(1, 4), (0, 4)],
        hover_cell       = handler.hover_cell,
        hover_wall       = handler.hover_wall,
        wall_horizontal  = handler.is_wall_horizontal,
        mode             = handler.current_mode
    )

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()