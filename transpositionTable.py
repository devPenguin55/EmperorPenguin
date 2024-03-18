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

    def hashState(self, state):
        return chess.polyglot.zobrist_hash(state)
    
    def store(self, state, flag, depth, value):
        self.table[self.hashState(state)] = entry(flag, depth, value)
        

    def lookup(self, state):
        return self.table.get(self.hashState(state), None)
    
    def clear(self):
        self.table = {}