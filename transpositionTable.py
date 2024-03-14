import chess

chess.Board.__hash__ = chess.polyglot.zobrist_hash

class entry:
    def __init__(self, flag, depth, value):
        self.flag = flag
        self.depth = depth
        self.value = value

class TT:
    def __init__(self):
        self.table = {}
    
    def store(self, state:chess.Board, flag, depth, value):
        self.table[state] = entry(flag, depth, value)

    def lookup(self, state:chess.Board):
        return self.table.get(state, None)