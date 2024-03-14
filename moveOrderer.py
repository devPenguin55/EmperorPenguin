import chess
import numpy as np

chess.Board.__hash__ = chess.polyglot.zobrist_hash


def orderMoves(self, state:chess.Board, moves, agent):
    statePromoted = state.promoted
    sortedMoves = np.empty((0, 2))
    for move in moves:
        moveEstimate = 0

        state.push(move)
        result = self.transpositionTable.get(state, None)
        if result == None:
            if state.promoted > statePromoted:
                moveEstimate += 30
            if state.is_stalemate():
                moveEstimate -= 40
            if len(list(state.legal_moves)) == 0:
                if state.turn == agent:
                    moveEstimate -= 10_000
                else:
                    moveEstimate += 10_000
            if state.is_check():
                if state.turn == agent:
                    moveEstimate -= 250
                else:
                    moveEstimate += 250
        else:
            moveEstimate = result

        sortedMoves = np.append(sortedMoves, np.array([[move, moveEstimate]]), axis=0)

        state.pop()
            
    # if state.turn == self.color:
    #     sortedMoves = sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
    # else:
    #     sortedMoves = sortedMoves[sortedMoves[:,1].argsort()][:,0]
    sortedMoves = sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
    return sortedMoves