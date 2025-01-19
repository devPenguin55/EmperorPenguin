import chess
import chess.polyglot as polyglot
import boardAndPieceEvaluationHelpers
from betterBoard import BetterBoard
import settings

chess.Board.__hash__ = chess.polyglot.zobrist_hash

# def isHanging(state, square):
#     attackers = state.moduleBoard.attackers(not state.moduleBoard.turn, square)
#     defenders = state.moduleBoard.attackers(state.moduleBoard.turn, square)
#     return len(attackers) > len(defenders)

# def evaluationFunction(self, state:BetterBoard, forceAgent=None):
#     agent = self.color # make it stay this way + for itself good, - for itself bad   for minimax search setup
#     if forceAgent:
#         agent = forceAgent
#     if state.moduleBoard.is_checkmate():
#         if state.moduleBoard.turn == agent:
#             return -self.CHECKMATE
#         else:
#             return self.CHECKMATE
#     elif state.moduleBoard.is_game_over(claim_draw=True):
#         # draw -> stalemate, repetition, etc.
#         # this is unfavorable for both sides so we can evaluate as losing a rook 
#         # (incentivize choosing another set of moves that does not result in game over by a form of draw)
    
#         return -state.pieces[chess.ROOK]

#     if state.phase == state.ENDGAME:
#         # move king close to other king to get checkmate in endgame
#         try:
#             kingDist = 20 * (1/(chess.square_distance(state.moduleBoard.king(agent), state.moduleBoard.king(not agent))))
#         except:
#             kingDist = 0
#         kingGame = self.kingEndGame
#     else:
#         kingDist = 0
#         kingGame = self.kingMiddleGame

#     mappedPieces = {
#         'p': self.pawns,
#         'n': self.knights,
#         'b': self.bishops,
#         'r': self.rooks,
#         'q': self.queen,
#         'k': kingGame
#     }
        
#     material = state.material
#     locationScore = state.locationScore

#     score = material*3 + locationScore/10 + kingDist*1.5
#     # score = material*3 + locationScore/10 + kingDist*1.25
    
#     if state.moduleBoard.is_check():
#         if state.moduleBoard.turn == agent:
#             # bot is in check
#             score -= chess.ROOK
#         else:
#             score += chess.PAWN * 2


    
    
#     # bishop pair
#     if len(state.moduleBoard.pieces(chess.BISHOP, agent)) == 2:
#         score += 2
#     else:
#         score -= 2

#     if len(state.moduleBoard.pieces(chess.BISHOP, not agent)) == 2:
#         score -= 2
#     else:
#         score += 2

#     # knight pair 
#     if len(state.moduleBoard.pieces(chess.KNIGHT, agent)) == 2:
#         score += 2
#     else:
#         score -= 2
 
#     if len(state.moduleBoard.pieces(chess.KNIGHT, not agent)) == 2:
#         score -= 2
#     else:
#         score += 2

#     # rook pair
#     if len(state.moduleBoard.pieces(chess.ROOK, agent)) == 2:
#         score += 2
#     else:
#         score -= 2
 
#     if len(state.moduleBoard.pieces(chess.ROOK, not agent)) == 2:
#         score -= 2
#     else:
#         score += 2


#     # ! old mobility score, I suppose it is bad now
#     # score += round(len(list(state.moduleBoard.legal_moves))**0.5, 1) # square root the legal moves so that many legal move amounts rounds out
#     # state.moduleBoard.turn = not state.moduleBoard.turn
#     # score -= round(len(list(state.moduleBoard.legal_moves))**0.5, 1)
#     # state.moduleBoard.turn = not state.moduleBoard.turn

#     if not state.moduleBoard.has_kingside_castling_rights(self.color):
#         score -= state.pieces[chess.ROOK] // 2
#     if not state.moduleBoard.has_queenside_castling_rights(self.color):
#         score -= state.pieces[chess.ROOK] // 2 

#     for square in state.moduleBoard.piece_map():
#         if isHanging(state, square):
#             piece = state.moduleBoard.piece_type_at(square)
#             if state.moduleBoard.color_at(square) == agent:
#                 score -= self.pieces[piece] * 0.5 # Penalty for hanging pieces

#     # score += (boardAndPieceEvaluationHelpers.pawnStructureScore(state, agent) - boardAndPieceEvaluationHelpers.pawnStructureScore(state, not agent)) 
#     # score += (boardAndPieceEvaluationHelpers.overallPieceProtectionScore(state, agent) - boardAndPieceEvaluationHelpers.overallPieceProtectionScore(state, not agent)) // 4
#     # score += (boardAndPieceEvaluationHelpers.passedPawnsScore(state, agent) - boardAndPieceEvaluationHelpers.passedPawnsScore(state, not agent)) 
#     # # score += round((boardAndPieceEvaluationHelpers.mobilityScore(state, self.color) - boardAndPieceEvaluationHelpers.mobilityScore(state, not self.color)) / 7, 1)
    
#     # score += boardAndPieceEvaluationHelpers.pieceSafetyAndStructureScore(state, self.color) - boardAndPieceEvaluationHelpers.pieceSafetyAndStructureScore(state, not self.color)

#     score /= self.pieces[chess.PAWN] 


#     # self.transpositionTable[state] = score
#     return score
    

def evaluationFunction(self, state:BetterBoard, forceAgent=None):
    agent = self.color if forceAgent is None else forceAgent

    if state.moduleBoard.is_checkmate():
        if state.moduleBoard.turn == agent:
            return -self.CHECKMATE
        else:
            return self.CHECKMATE
    elif state.moduleBoard.is_game_over(claim_draw=True):
        # draw -> stalemate, repetition, etc.
        # this is unfavorable for both sides so we can evaluate as losing a rook 
        # (incentivize choosing another set of moves that does not result in game over by a form of draw)
    
        return -state.pieces[chess.ROOK]

    # Calculate base material and position scores
    material = state.material
    locationScore = state.locationScore
    
    # Add piece safety evaluation
    safety_score = 0
    for square, piece in state.moduleBoard.piece_map().items():
        is_agent_piece = state.moduleBoard.color_at(square) == agent
        attackers = state.moduleBoard.attackers(not state.moduleBoard.color_at(square), square)
        defenders = state.moduleBoard.attackers(state.moduleBoard.color_at(square), square)
        
        # Penalize hanging pieces heavily
        piece_type = state.moduleBoard.piece_type_at(square)
        piece_value = self.pieces[piece_type]
        if len(attackers) > len(defenders):
            safety_score += -piece_value if is_agent_piece else piece_value

        # Penalize undefended pieces
        if len(defenders) == 0 and piece_type != chess.KING:
            safety_score += -piece_value/4 if is_agent_piece else piece_value/4


    if state.phase == state.ENDGAME:
        try:
            kingDist = 20 * (1/(chess.square_distance(state.moduleBoard.king(agent), state.moduleBoard.king(not agent))))
        except:
            kingDist = 0
        kingGame = self.kingEndGame
    else:
        kingDist = 0
        kingGame = self.kingMiddleGame

    # combine scores with better weights
    score = (material * 10 +               # Increase material importance
             locationScore/10 +            # Keep positional score moderate
             safety_score * 2 +            # Add significant weight to piece safety
             kingDist * 1.5)              # Keep king distance similar

    # Additional evaluation terms
    if state.moduleBoard.is_check():
        score += -50 if state.moduleBoard.turn == agent else 20

    # Bishop/Knight pair bonuses (keep small relative to material)
    for piece_type in [chess.BISHOP, chess.KNIGHT, chess.ROOK]:
        if len(state.moduleBoard.pieces(piece_type, agent)) == 2:
            score += 20
        if len(state.moduleBoard.pieces(piece_type, not agent)) == 2:
            score -= 20

    # Scale the final score to pawn units, but don't divide by full pawn value
    score /= (self.pieces[chess.PAWN] / 2)  # This makes material count for more

    return score