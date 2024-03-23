import chess
import chess.polyglot as polyglot
from betterBoard import BetterBoard

chess.Board.__hash__ = chess.polyglot.zobrist_hash


def evaluationFunction(self, state:BetterBoard):
    agent = self.color # make it stay this way 
    if state.moduleBoard.is_checkmate():
        if state.moduleBoard.turn == agent:
            return -self.CHECKMATE
        else:
            return self.CHECKMATE
        
    # check if in endgame 
    inEndgame = False
    # no queens
    if state.moduleBoard.pieces(chess.QUEEN, agent) == 0 and state.moduleBoard.pieces(chess.QUEEN, not agent) == 0:
        inEndgame = True

    if not inEndgame:
        kingDist = 0
        kingGame = self.kingMiddleGame
    else:
        # move king close to other king to get checkmate in endgame
        try:
            kingDist = 20 * (1/(chess.square_distance(state.moduleBoard.king(agent), state.moduleBoard.king(not agent))))
        except:
            kingDist = 0
        kingGame = self.kingEndGame

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

    if len(state.moduleBoard.pieces(chess.BISHOP, agent)) == 2:
        score += chess.BISHOP//2
    else:
        score -= chess.BISHOP//2

    if len(state.moduleBoard.pieces(chess.BISHOP, not agent)) == 2:
        score -= chess.BISHOP//2
    else:
        score += chess.BISHOP//2

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