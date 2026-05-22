# 🏆 Quoridor — Python Pygame Implementation

> A complete implementation of the award-winning abstract strategy board game **Quoridor**, built with Python and Pygame. Features a fully playable GUI, intelligent AI opponents at three difficulty levels, and undo/redo functionality.

---

## 📸 Screenshots

| Menu Screen | Gameplay | AI Match |
|-------------|----------|----------|
| ![Menu](assets/screenshot_menu.png) | ![Game](assets/screenshot_game.png) | ![AI](assets/screenshot_ai.png) |

---

## 🎮 Game Description

Quoridor is a strategy board game invented by **Mirko Marchesi** in 1997, winner of the **Mensa Mind Game award**. Two players compete on a 9×9 grid, each trying to move their pawn to the opposite side before their opponent does. On each turn, a player must either:

- **Move** their pawn one square orthogonally
- **Place a wall** to block the opponent's path

The catch — walls cannot completely trap a player. There must always be at least one valid path to the goal. This creates deep strategic tension between racing forward and blocking your opponent.

---

## ✨ Features

- ✅ Complete Quoridor ruleset for 2 players
- ✅ Human vs Human local multiplayer
- ✅ Human vs AI with 3 difficulty levels
- ✅ Valid move highlighting
- ✅ Wall placement preview on hover
- ✅ Undo / Redo (unlimited)
- ✅ Turn indicator and wall count display
- ✅ Win screen with game over overlay
- ✅ Game reset and return to menu
- ✅ Clean dark-themed GUI

---

## 🤖 AI Difficulty Levels

| Level | Algorithm | Description |
|-------|-----------|-------------|
| **Easy** | Greedy | Moves toward goal each turn, places random walls occasionally |
| **Medium** | BFS Heuristic | Uses pathfinding to pick the best move, places walls to slow opponent |
| **Hard** | Minimax + Alpha-Beta Pruning | Thinks 3 moves ahead, evaluates all possible outcomes, plays optimally |

---

## 🗂️ Project Structure

```
quoridor/
├── main.py               # Entry point — menu + game loop
├── config.py             # All constants and colors
├── game/
│   ├── __init__.py       # Game class — top level state
│   ├── board.py          # Wall storage and movement blocking
│   ├── player.py         # Player state and goal tracking
│   ├── rules.py          # Move validation and rule enforcement
│   └── game_state.py     # Snapshot system for undo/redo
├── ai/
│   ├── __init__.py       # make_ai() factory function
│   ├── easy_lvl.py       # Easy AI — greedy movement
│   ├── medium_lvl.py     # Medium AI — BFS guided
│   └── hard_lvl.py       # Hard AI — Minimax with alpha-beta
├── gui/
│   ├── __init__.py
│   ├── renderer.py       # Draws board, pawns, walls, sidebar, UI
│   └── input_handler.py  # Mouse and keyboard input processing
├── utils/
│   ├── __init__.py
│   ├── pathfinding.py    # BFS shortest path and valid move generation
│   └── history.py        # Undo/redo stack engine
└── assets/               # Screenshots and media
```

---

## 🔧 Installation

### Requirements
- Python 3.8 or higher
- Pygame 2.0 or higher

### Step 1 — Clone the repository
```bash
git clone https://github.com/yourusername/quoridor.git
cd quoridor
```

### Step 2 — Install dependencies
```bash
pip install pygame
```

### Step 3 — Run the game
```bash
python main.py
```

---

## 🕹️ Controls

| Input | Action |
|-------|--------|
| `Left Click` on cell | Move pawn to that cell |
| `Left Click` on wall slot | Place wall |
| `Right Click` | Rotate wall orientation |
| `M` | Switch to Move mode |
| `W` | Switch to Wall mode |
| `R` | Rotate wall orientation |
| `Ctrl + Z` | Undo last move |
| `Ctrl + Y` | Redo last move |
| `F5` | Reset / New game |
| `Escape` | Return to main menu |

---

## 📐 How to Play

1. **Launch the game** and select a mode from the menu
2. **Player 1 (Red)** starts at the top center, goal is the bottom row
3. **Player 2 (Blue)** starts at the bottom center, goal is the top row
4. Each turn — either **move your pawn** or **place a wall**
5. Pawns move one square orthogonally (up, down, left, right)
6. If your pawn is adjacent to the opponent, you can **jump over** them
7. If a jump is blocked by a wall, you can move **diagonally** around them
8. Walls are **2 squares long** and block movement between cells
9. A wall **cannot** be placed if it completely blocks any player's path
10. First player to reach the opposite side **wins**

---

## 🧠 Technical Details

### Pathfinding
Wall legality is enforced using **Breadth-First Search (BFS)**. After every attempted wall placement, BFS checks that both players still have at least one valid path to their goal row. If either player is blocked, the wall placement is rejected.

### Undo / Redo
Every move (pawn or wall) pushes a full **game state snapshot** onto an undo stack before applying the move. Undoing pops the snapshot and restores the game. Redoing re-applies it. The redo stack clears whenever a new move is made.

### Minimax AI
The Hard AI uses **Minimax with Alpha-Beta Pruning** at depth 3. The evaluation function is:

```
score = opponent_distance_to_goal - my_distance_to_goal
```

A higher score means the AI is closer to winning relative to the opponent. Alpha-beta pruning cuts branches that cannot affect the final decision, making the search fast enough for real-time play.

---

## 👥 Team

| Member | Role |
|--------|------|
| Member 1 | Core Engine — Board, Player, Rules, History |
| Member 2 | State & Pathfinding — BFS, Game State Snapshots |
| Member 3 | AI Opponents — Easy, Medium, Hard |
| Member 4 | GUI — Renderer, Input Handler |
| Member 5 | Integration, Main Loop, Documentation |

---

## 🎥 Demo Video

▶️ [Watch the demo video here](https://youtu.be/your-video-link)

The video covers:
- Game setup and UI overview
- Human vs Human gameplay
- Human vs Easy, Medium, and Hard AI
- Undo/Redo demonstration

---

## 📚 References

- [Official Quoridor Rules](https://en.gigamic.com/files/media/fiche_pedagogique/educative-sheet_quoridor_en.pdf)
- [Quoridor on BoardGameGeek](https://boardgamegeek.com/boardgame/624/quoridor)
- [Minimax Algorithm — Wikipedia](https://en.wikipedia.org/wiki/Minimax)
- [Alpha-Beta Pruning — Wikipedia](https://en.wikipedia.org/wiki/Alpha%E2%80%93beta_pruning)
- [BFS Pathfinding — Wikipedia](https://en.wikipedia.org/wiki/Breadth-first_search)
- [Pygame Documentation](https://www.pygame.org/docs/)

---

## 📄 License

This project was developed as an academic assignment. All game logic and implementation are original work by the team.