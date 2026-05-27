# Board
BOARD_SIZE = 9
CELL_SIZE = 64
WALL_THICKNESS = 8
WALL_LENGTH = CELL_SIZE - 4
BOARD_OFFSET_X = 40
BOARD_OFFSET_Y = 100

# Window
SIDEBAR_WIDTH = 260
WINDOW_WIDTH = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET_X * 2 + SIDEBAR_WIDTH
WINDOW_HEIGHT = BOARD_SIZE * CELL_SIZE + BOARD_OFFSET_Y + 60
FPS = 60

# ── Light theme colors ────────────────────────────────────────────────────────
# Background
C_BG         = (242, 238, 229)   # warm cream page background
C_BOARD_BG   = (255, 252, 245)   # near-white board panel

# Cells
C_CELL       = (250, 247, 240)   # light wood-cream cell
C_CELL_HOVER = (210, 230, 200)   # soft green hover
C_GRID       = (195, 185, 165)   # warm tan grid lines

# Valid move highlight
C_VALID_MOVE = (130, 195, 100)   # muted green

# Wall slots (shown as subtle dots in wall mode)
C_WALL_SLOT  = (195, 185, 165)   # same as grid — subtle
C_WALL_HOVER = (200, 130, 40)    # amber preview

# Placed walls
C_WALL_PLACED= (130, 85,  35)    # dark wood-brown

# Wall ghost per player
C_WALL_P1    = (205, 70,  60)    # red tint for P1 ghost
C_WALL_P2    = (55,  110, 200)   # blue tint for P2 ghost

# Pawns
C_P1         = (210, 65,  55)    # red pawn fill
C_P2         = (50,  105, 195)   # blue pawn fill
C_P1_BORDER  = (240, 130, 120)   # lighter red ring
C_P2_BORDER  = (120, 175, 240)   # lighter blue ring

# Text
C_TEXT       = (40,  32,  20)    # near-black warm
C_TEXT_DIM   = (130, 118, 95)    # muted tan

# Accent (headings, highlights)
C_ACCENT     = (160, 100, 25)    # dark amber / warm gold

# Sidebar
C_SIDEBAR_BG = (235, 230, 218)   # slightly darker than board bg

# Buttons
C_BTN        = (215, 208, 192)   # light tan button
C_BTN_HOVER  = (195, 188, 170)   # slightly darker on hover
C_BTN_ACTIVE = (180, 135, 70)    # warm amber active state

# Win overlay
C_WIN_OVERLAY= (0, 0, 0, 160)

# Players
PLAYER_RADIUS = 22
P1_START = (0, 4)
P2_START = (8, 4)
P1_GOAL_ROW = 8
P2_GOAL_ROW = 0
WALLS_PER_PLAYER = 10

# AI
AI_THINK_DELAY = 400