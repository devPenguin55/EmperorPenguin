import chess
import chess.polyglot as polyglot
import boardAndPieceEvaluationHelpers
from betterBoard import BetterBoard
import settings

chess.Board.__hash__ = chess.polyglot.zobrist_hash


def evaluationFunction(self, state:BetterBoard, forceAgent=None):
    agent = self.color # make it stay this way + for itself good, - for itself bad   for minimax search setup
    if forceAgent:
        agent = forceAgent
    if state.moduleBoard.is_checkmate():
        if state.moduleBoard.turn == agent:
            return -self.CHECKMATE
        else:
            return self.CHECKMATE
    elif state.moduleBoard.is_game_over():
        # draw -> stalemate, repetition, etc.
        # this is unfavorable so we can evaluate as losing a rook (pretty bad)
        return -state.pieces[chess.ROOK]


    if state.phase == state.ENDGAME:
        # move king close to other king to get checkmate in endgame
        try:
            kingDist = 20 * (1/(chess.square_distance(state.moduleBoard.king(agent), state.moduleBoard.king(not agent))))
        except:
            kingDist = 0
        kingGame = self.kingEndGame
    else:
        kingDist = 0
        kingGame = self.kingMiddleGame

    mappedPieces = {
        'p': self.pawns,
        'n': self.knights,
        'b': self.bishops,
        'r': self.rooks,
        'q': self.queen,
        'k': kingGame
    }
        
    material = state.material
    locationScore = state.locationScore
    locationScore = 0

    score = material*3 + locationScore/10 + kingDist*1.25
    # score = material*5 + locationScore/10 + kingDist*0.5
    
    if state.moduleBoard.is_check():
        if state.moduleBoard.turn == agent:
            # bot is in check
            score -= chess.ROOK
        else:
            score += chess.PAWN * 2

    if len(state.moduleBoard.pieces(chess.BISHOP, agent)) == 2:
        score += chess.BISHOP//2
    else:
        score -= chess.BISHOP//2

    if len(state.moduleBoard.pieces(chess.BISHOP, not agent)) == 2:
        score -= chess.BISHOP//2
    else:
        score += chess.BISHOP//2

    score += len(list(state.moduleBoard.legal_moves))
    state.moduleBoard.turn = not state.moduleBoard.turn**0.5 # square root the legal moves so that many legal move amounts rounds out
    score -= len(list(state.moduleBoard.legal_moves))
    state.moduleBoard.turn = not state.moduleBoard.turn**0.5

    score += (boardAndPieceEvaluationHelpers.pawnStructureScore(state, agent) - boardAndPieceEvaluationHelpers.pawnStructureScore(state, not agent)) * 0.6 
    score += (boardAndPieceEvaluationHelpers.overallPieceProtectionScore(state, agent) - boardAndPieceEvaluationHelpers.overallPieceProtectionScore(state, not agent)) * 5
    score += (boardAndPieceEvaluationHelpers.passedPawnsScore(state, agent) - boardAndPieceEvaluationHelpers.passedPawnsScore(state, not agent)) * 1


    score /= self.pieces[chess.PAWN]

    # self.transpositionTable[state] = score
    return score
    

# version with transposition table inside of eval function
# def evaluationFunction(self, state:chess.Board):
#     agent = self.color
#     if state.is_checkmate():
#         if state.turn == agent:
#             return -self.CHECKMATE
#         else:
#             return self.CHECKMATE
    
#     result = self.transpositionTable.get(state, None)
#     if result != None:
#         return result
#     else:
#         inEndgame = state.pieces(chess.QUEEN, agent) == 0 and state.pieces(chess.QUEEN, not agent) == 0

#         if not inEndgame:
#             kingDist = 0
#             kingGame = self.kingMiddleGame
#         else:
#             # move king close to other king to get checkmate in endgame
#             try:
#                 kingDist = 20 * (1/(chess.square_distance(state.king(agent), state.king(not agent))))
#             except:
#                 kingDist = 0
#             kingGame = self.kingEndGame

#         mappedPieces = {
#             'p': self.pawns,
#             'n': self.knights,
#             'b': self.bishops,
#             'r': self.rooks,
#             'q': self.queen,
#             'k': kingGame
#         }
            
#         pieceMap = state.piece_map()

#         def transformIndex(index):
#             # get row and column
#             row = index // 8
#             col = index % 8
    
#             # get the new row
#             newRow = 7 - row
    
#             # find new index
#             newIndex = newRow * 8 + col
    
#             return newIndex
        
#         locationScore = 0
#         material = 0
#         for index in pieceMap:
#             piece, index = str(pieceMap[index]), index
                
#             if agent == True and piece == piece.lower():
#                 side = -1
#             elif agent == False and piece == piece.upper():
#                 side = -1
#             else:
#                 side = 1

#             pieceChessType = self.stringToPiece[piece.lower()]
#             table = mappedPieces[piece.lower()]
#             locationScore += table[transformIndex(index)] * side
#             material += self.pieces[pieceChessType] * side

            
#         score = material*5 + locationScore/10 + kingDist*6
#         # score = material*3 + locationScore/10 + kingDist*0.5
        
#         if state.is_check():
#             if state.turn == agent:
#                 # bot is in check
#                 score -= chess.ROOK

#         if len(state.pieces(chess.BISHOP, agent)) == 2:
#             score += chess.BISHOP
#         else:
#             score -= chess.BISHOP

#         score /= self.pieces[chess.PAWN]
#         self.transpositionTable[state] = score
#         return score