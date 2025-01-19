import chess
import numpy as np
from betterBoard import BetterBoard
import transpositionTableNEW
import settings
chess.Board.__hash__ = chess.polyglot.zobrist_hash


def orderMoves(self, state: BetterBoard, moves: chess.LegalMoveGenerator, agent, depth, inQSearch=False):
    ply = self.currentTopDepth - depth

    orderedMoves = list(moves)
    actualKillerMoves = []
    actualPvMoves = []

    if inQSearch:
        ttEntry = self.qSearchTranspositionTable.lookup(state.moduleBoard)
    else:
        ttEntry = self.transpositionTable.lookup(state.moduleBoard)
    if ttEntry and ttEntry.bestMove:
        ttBestMove = [ttEntry.bestMove]
    else:
        ttBestMove = []

    pvMoves = [i[0] for i in self.PV]
    for move in orderedMoves:
        if move in self.killers[ply]:
            actualKillerMoves.append(move)
        elif move in pvMoves:
            actualPvMoves.append(move)

    lessImportantMoves = []
    for move in orderedMoves:
        if move not in actualKillerMoves and move not in actualPvMoves:
            if state.moduleBoard.is_capture(move):
                attacker = self.MVV_LVA_INDEX_CONVERSION[state.moduleBoard.piece_type_at(move.from_square)]
                victim = self.MVV_LVA_INDEX_CONVERSION[state.moduleBoard.piece_type_at(move.to_square)]
                score = self.MVV_LVA_TABLE[victim][attacker]
            else:
                score = 0
                # score = self.historyMoves[state.moduleBoard.piece_type_at(move.from_square)-1][move.to_square] >> 2
            lessImportantMoves.append((move, score))

    lessImportantMoves.sort(key=lambda x: x[-1], reverse=True)
    lessImportantMoves = [i[0] for i in lessImportantMoves]

    return ttBestMove + actualKillerMoves + actualPvMoves + lessImportantMoves

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
