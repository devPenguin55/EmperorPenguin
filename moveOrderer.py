import chess
import numpy as np
from betterBoard import BetterBoard

chess.Board.__hash__ = chess.polyglot.zobrist_hash


def orderMoves(self, state:BetterBoard, moves, agent):
    sortedMoves = np.empty((0, 2))
    for move in moves:
        moveEstimate = 0
        state.push(move)
        moveEstimate += 10*state.moduleBoard.promoted
        if state.moduleBoard.is_stalemate():
            moveEstimate -= 40
        if len(list(state.moduleBoard.legal_moves)) == 0:
            if state.moduleBoard.turn == agent:
                moveEstimate -= 100_000
            else:
                moveEstimate += 100_000
        if state.moduleBoard.is_check():
            if state.moduleBoard.turn == agent:
                moveEstimate -= 250

        sortedMoves = np.append(sortedMoves, np.array([[move, moveEstimate]]), axis=0)

        state.pop()
            
    # if state.turn == self.color:
    #     return sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
    # else:
    #     return sortedMoves[sortedMoves[:,1].argsort()][:,0]
    return sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]