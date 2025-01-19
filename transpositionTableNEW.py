import chess
import chess.polyglot
from copy import deepcopy
import settings

chess.Board.__hash__ = chess.polyglot.zobrist_hash

class entry:
    def __init__(self, flag, depth, value, bestMove, currentAge):
        self.flag = flag
        self.depth = depth
        self.value = value
        self.bestMove = bestMove
        self.currentAge = currentAge

class TT:
    def __init__(self, sharedMemory):
        self.table = sharedMemory

    def hashState(self, state):
        return chess.polyglot.zobrist_hash(state)
    
    def store(self, state, flag, depth, value, bestMove, currentAge):
        okayStore = False
        existingEntry = self.table.get(self.hashState(state), None)
        if existingEntry:
            # if this state exists in the table and the new entry has better depth, overwrite it
            if depth >= existingEntry.depth:
                okayStore = True
        else:
            okayStore = True

        if okayStore:
            self.table[self.hashState(state)] = entry(flag, depth, value, bestMove, currentAge)
        

    def lookup(self, state, isAlreadyHashed=False):
        if isAlreadyHashed:
            return self.table.get(state, None)
        return self.table.get(self.hashState(state), None)
    
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