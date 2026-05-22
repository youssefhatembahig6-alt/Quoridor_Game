from ai.easy_lvl import EasyAI
from ai.medium_lvl import MediumAI
from ai.hard_lvl import HardAI

def make_ai(difficulty: str, pid: int):
    d = difficulty.lower()
    if d == 'easy':
        return EasyAI(pid)
    elif d == 'medium':
        return MediumAI(pid)
    elif d == 'hard':
        return HardAI(pid)
    raise ValueError(f"Unknown difficulty: {difficulty}")