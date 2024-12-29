import chess
import numpy as np
from betterBoard import BetterBoard
from evaluation import evaluationFunction
import transpositionTable
import settings
chess.Board.__hash__ = chess.polyglot.zobrist_hash


def orderMoves(self, state:BetterBoard, moves, agent, depth, pv, tt:transpositionTable.TT, killerMoves):
    self.pieces = {
        chess.KING: 200,
        chess.QUEEN: 90,
        chess.ROOK: 50,
        chess.BISHOP: 30,
        chess.KNIGHT: 30,
        chess.PAWN: 10,
    }

    # captureMoves = []
    # nonCaptureMoves = []

    # for move in moves:
    #     if state.moduleBoard.is_capture(move):
    #         captureMoves.append(move)
    #     else:
    #         nonCaptureMoves.append(move)

    # orderedMoves = captureMoves + nonCaptureMoves
    orderedMoves = list(moves)

    pvMoves = [i[0] for i in pv]
    for move in orderedMoves:
        state.push(move)
        ttEntry = tt.lookup(state.moduleBoard)
        if ttEntry is not None and ttEntry.depth <= depth:

            while move in orderedMoves:
                orderedMoves.remove(move)

            orderedMoves = [move] + orderedMoves
        state.pop()

        if move in pvMoves:
            pvDepth = pv[pvMoves.index(move)][1]
            while move in orderedMoves:
                orderedMoves.remove(move)

            orderedMoves = [move] + orderedMoves

        if move in killerMoves:
            while move in orderedMoves:
                orderedMoves.remove(move)

            orderedMoves = [move] + orderedMoves

    return orderedMoves

# def orderMoves(self, state:BetterBoard, moves, agent, depth):
#     sortedMoves = np.empty((0, 2))
#     for move in moves:

#         moveEstimate = 0
#         state.push(move)
#         # ttEntry = self.transpositionTable.lookup(state.moduleBoard)
#         # if ttEntry is not None and ttEntry.depth >= depth:
#         #     self.transpositionMatches += 1
#         #     moveEstimate = ttEntry.value
#         # else:
#         #     moveEstimate += 10*state.moduleBoard.promoted
#         #     if state.moduleBoard.is_stalemate():
#         #         moveEstimate -= 40
#         #     if len(list(state.moduleBoard.legal_moves)) == 0:
#         #         if state.moduleBoard.turn == agent:
#         #             moveEstimate -= 100_000
#         #         else:
#         #             moveEstimate += 100_000
#         #     if state.moduleBoard.is_check():
#         #         if state.moduleBoard.turn == agent:
#         #             moveEstimate -= 250
#         moveEstimate = state.material*3 + state.locationScore/10

#         sortedMoves = np.append(sortedMoves, np.array([[move, moveEstimate]]), axis=0)

#         state.pop()
            
#     # if state.turn == self.color:
#     #     return sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
#     # else:
#     #     return sortedMoves[sortedMoves[:,1].argsort()][:,0]
#     return sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]