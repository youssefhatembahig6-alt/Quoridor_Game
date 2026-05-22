from config import WALLS_PER_PLAYER, P1_START, P2_START, P1_GOAL_ROW, P2_GOAL_ROW

class Player:
    def __init__(self, pid: int):
        self.pid = pid           # 1 or 2
        self.row, self.col = (P1_START if pid == 1 else P2_START)
        self.walls_left = WALLS_PER_PLAYER
        self.goal_row = P1_GOAL_ROW if pid == 1 else P2_GOAL_ROW

    def copy(self):
        p = Player.__new__(Player)
        p.pid = self.pid
        p.row = self.row
        p.col = self.col
        p.walls_left = self.walls_left
        p.goal_row = self.goal_row
        return p

    def has_won(self) -> bool:
        return self.row == self.goal_row

    def __repr__(self):
        return f"Player({self.pid}, pos=({self.row},{self.col}), walls={self.walls_left})"
