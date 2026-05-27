import sys
import pygame

from config import (
    WINDOW_WIDTH, WINDOW_HEIGHT, FPS, AI_THINK_DELAY,
    C_BG, C_BTN_ACTIVE, C_ACCENT, C_TEXT_DIM,
)
from game          import Game
from game.rules    import Rules
from utils.history import History
from gui.renderer      import Renderer
from gui.input_handler import InputHandler
from ai import make_ai


# ══════════════════════════════════════════════
#  MENU
# ══════════════════════════════════════════════

def _draw_menu(screen, fonts, buttons, hover_idx):
    screen.fill((242, 238, 229))

    cx = WINDOW_WIDTH // 2
    title = fonts['title'].render("QUORIDOR", True, (160, 100, 25))
    sub   = fonts['medium'].render(
        "An abstract strategy game by Mirko Marchesi", True, (130, 118, 95))
    screen.blit(title, (cx - title.get_width() // 2, 100))
    screen.blit(sub,   (cx - sub.get_width()   // 2, 150))

    pygame.draw.line(screen, (195, 185, 165), (cx-160, 185), (cx+160, 185), 1)

    label = fonts['small'].render("SELECT GAME MODE", True, (130, 118, 95))
    screen.blit(label, (cx - label.get_width() // 2, 205))

    for i, (text, _) in enumerate(buttons):
        rect = pygame.Rect(cx - 180, 240 + i * 64, 360, 48)
        color = (180, 135, 70) if i == hover_idx else (215, 208, 192)
        pygame.draw.rect(screen, color, rect, border_radius=8)
        if i == hover_idx:
            pygame.draw.rect(screen, (160, 100, 25), rect, width=2, border_radius=8)
        surf = fonts['medium'].render(
            text, True, (255,255,255) if i == hover_idx else (40, 32, 20))
        screen.blit(surf, (rect.centerx - surf.get_width()  // 2,
                           rect.centery - surf.get_height() // 2))

    footer = fonts['small'].render("Press Esc to quit", True, (130, 118, 95))
    screen.blit(footer, (cx - footer.get_width() // 2, WINDOW_HEIGHT - 40))


def run_menu(screen):
    pygame.font.init()
    fonts = {
        'title':  pygame.font.SysFont("segoeui", 48, bold=True),
        'medium': pygame.font.SysFont("segoeui", 22),
        'small':  pygame.font.SysFont("segoeui", 16),
    }
    buttons = [
        ("Human vs Human",          ('hvh',)),
        ("Human vs AI  —  Easy",    ('hvai', 'easy')),
        ("Human vs AI  —  Medium",  ('hvai', 'medium')),
        ("Human vs AI  —  Hard",    ('hvai', 'hard')),
    ]
    clock = pygame.time.Clock()
    cx    = WINDOW_WIDTH // 2

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return None
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                for i, (_, result) in enumerate(buttons):
                    if pygame.Rect(cx-180, 240+i*64, 360, 48).collidepoint(mx, my):
                        return result

        mx, my    = pygame.mouse.get_pos()
        hover_idx = next(
            (i for i in range(len(buttons))
             if pygame.Rect(cx-180, 240+i*64, 360, 48).collidepoint(mx, my)),
            -1
        )
        _draw_menu(screen, fonts, buttons, hover_idx)
        pygame.display.flip()
        clock.tick(FPS)


# ══════════════════════════════════════════════
#  GAME LOOP
# ══════════════════════════════════════════════

def run_game(screen, mode, difficulty=None):
    game    = Game()
    history = History()
    rules   = Rules(game, history)
    renderer = Renderer(screen)

    ai = make_ai(difficulty, pid=2) if mode == 'hvai' else None

    ai_timer_start  = None
    ai_move_pending = False
    reset_requested = False
    menu_requested  = False

    def on_reset():
        nonlocal reset_requested; reset_requested = True
    def on_menu():
        nonlocal menu_requested;  menu_requested  = True

    # Pass renderer so InputHandler can detect sidebar button clicks
    handler = InputHandler(rules=rules, renderer=renderer,
                           on_reset=on_reset, on_menu=on_menu)
    clock   = pygame.time.Clock()

    while True:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

        if reset_requested:
            game.reset(); history.clear()
            handler._reset_ui_state()
            ai_timer_start = None; ai_move_pending = False
            reset_requested = False
            continue

        if menu_requested:
            return

        # ── Always handle input (keyboard shortcuts work even on win screen) ──
        is_ai_turn = (ai is not None and game.current_turn == ai.pid)
        handler.handle(events, game, allow_board_click=not is_ai_turn)

        # ── AI turn ──────────────────────────────────────────────────────────
        if ai and not game.winner:
            if game.current_turn == ai.pid:
                now = pygame.time.get_ticks()
                if not ai_move_pending:
                    ai_timer_start  = now
                    ai_move_pending = True
                elif now - ai_timer_start >= AI_THINK_DELAY:
                    move = ai.choose_move(game)
                    if move['type'] == 'pawn':
                        rules.try_move_pawn(move['row'], move['col'])
                    else:
                        rules.try_place_wall(
                            move['row'], move['col'], move['horizontal'])
                    ai_move_pending = False
            else:
                ai_move_pending = False

        # ── Draw ─────────────────────────────────────────────────────────────
        valid_moves = [] if game.winner else rules.valid_pawn_moves()
        renderer.draw_frame(
            game            = game,
            valid_moves     = valid_moves,
            hover_cell      = handler.hover_cell,
            hover_wall      = handler.hover_wall,
            wall_horizontal = handler.is_wall_horizontal,
            mode            = handler.current_mode,
            hover_btn       = handler.hover_sidebar_btn,
        )

        if ai_move_pending:
            _draw_thinking(screen, renderer)

        pygame.display.flip()
        clock.tick(FPS)


def _draw_thinking(screen, renderer):
    font = pygame.font.SysFont("segoeui", 16)
    surf = font.render("  AI is thinking…  ", True, (160, 100, 25))
    x, y = renderer.sb_x + 20, WINDOW_HEIGHT - 50
    bg = pygame.Rect(x-4, y-4, surf.get_width()+8, surf.get_height()+8)
    pygame.draw.rect(screen, (215, 208, 192), bg, border_radius=6)
    screen.blit(surf, (x, y))


# ══════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════

def main():
    pygame.init()
    pygame.display.set_caption("Quoridor")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    icon = pygame.Surface((32, 32)); icon.fill((160, 100, 25))
    pygame.display.set_icon(icon)

    while True:
        result = run_menu(screen)
        if result is None:
            break
        run_game(screen, result[0], result[1] if len(result) > 1 else None)

    pygame.quit(); sys.exit()


if __name__ == "__main__":
    main()