import chess
import chess.polyglot
from copy import deepcopy
import settings

chess.Board.__hash__ = chess.polyglot.zobrist_hash

class entry:
    def __init__(self, flag, depth, value):
        self.flag = flag
        self.depth = depth
        self.value = value

    def toDict(self):
        return {'flag': self.flag, 'depth':self.depth, 'value':self.value}
    
    @staticmethod
    def fromDict(data):
        return entry(data['flag'], data['depth'], data['value'])

class TT:
    def __init__(self, sharedMemory):
        self.table = sharedMemory

    def hashState(self, state):
        return chess.polyglot.zobrist_hash(state)
    
    def store(self, state, flag, depth, value):
        self.table[self.hashState(state)] = entry(flag, depth, value).toDict()
        

    def lookup(self, state):
        result = self.table.get(self.hashState(state), None)
        return entry.fromDict(result) if result else None
    
    def clear(self):
        self.table.clear()

    def copy(self):
        return deepcopy(self)

    def __len__(self):
        return len(self.table)
    

# import chess
# import chess.polyglot

# chess.Board.__hash__ = chess.polyglot.zobrist_hash

# class entry:
#     def __init__(self, flag, depth, value):
#         self.flag = flag
#         self.depth = depth
#         self.value = value

# class TT:
#     def __init__(self):
#         self.table = {}

#     def hashState(self, state):
#         return chess.polyglot.zobrist_hash(state)
    
#     def store(self, state, flag, depth, value):
#         self.table[self.hashState(state)] = entry(flag, depth, value)
        

#     def lookup(self, state):
#         return self.table.get(self.hashState(state), None)
    
#     def clear(self):
#         self.table.clear()

#     def __len__(self):
#         return len(self.table)