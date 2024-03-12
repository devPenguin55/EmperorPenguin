import chess
import numpy as np

def orderMoves(self, state:chess.Board, moves, agent):
    statePromoted = state.promoted
    sortedMoves = np.empty((0, 2))
    killers, states = [], []
    for killer, curState in self.killers:
        killers.append(killer)
        states.append(curState)
    for move in moves:
        moveEstimate = 0

        # if state.gives_check(move):
        #     # opponent in check pos
        #     moveEstimate += 10
        # if state.is_into_check(move):
        #     # current side into check neg
        #     moveEstimate += -250
        state.push(move)
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
        if state in states and move in killers:
           moveEstimate += 100

        sortedMoves = np.append(sortedMoves, np.array([[move, moveEstimate]]), axis=0)

        state.pop()
            
    # if state.turn == self.color:
    #     sortedMoves = sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
    # else:
    #     sortedMoves = sortedMoves[sortedMoves[:,1].argsort()][:,0]
    sortedMoves = sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
    return sortedMoves