class History:
    #undo/redo stack storing 

    def __init__(self):
        self._undo_stack = []
        self._redo_stack = []

    def push(self, snapshot):
        self._undo_stack.append(snapshot)
        self._redo_stack.clear()

    def undo(self):
        if not self._undo_stack:
            return None
        snapshot = self._undo_stack.pop()
        self._redo_stack.append(snapshot)
        return snapshot

    def redo(self):
        if not self._redo_stack:
            return None
        snapshot = self._redo_stack.pop()
        self._undo_stack.append(snapshot)
        return snapshot

    def can_undo(self) -> bool:
        return len(self._undo_stack) > 0

    def can_redo(self) -> bool:
        return len(self._redo_stack) > 0

    def clear(self):
        self._undo_stack.clear()
        self._redo_stack.clear()