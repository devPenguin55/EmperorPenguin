import chess
import chess.polyglot as polyglot

def evaluationFunction(self, state:chess.Board):
    hashed = polyglot.zobrist_hash(state)

    if hashed in self.transpositionTable:
        return self.transpositionTable[hashed]
    else:
        inEndgame = state.pieces(chess.QUEEN, self.color) == 0 and state.pieces(chess.QUEEN, not self.color) == 0

        if not inEndgame:
            kingDist = 0
            kingGame = self.kingMiddleGame
        else:
            # move king close to other king to get checkmate in endgame
            try:
                kingDist = 20 * (1/(chess.square_distance(state.king(self.color), state.king(not self.color))))
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
            
        pieceMap = state.piece_map()

        def transformIndex(index):
            # Calculate row and column in the bottom layout
            row = index // 8
            col = index % 8
    
            # Calculate row in the top layout
            newRow = 7 - row
    
            # Calculate index in the top layout
            newIndex = newRow * 8 + col
    
            return newIndex
        
        locationScore = 0
        material = 0
        for index in pieceMap:
            piece, index = str(pieceMap[index]), index
                
            if self.color == True and piece == piece.lower():
                side = -1
            elif self.color == False and piece == piece.upper():
                side = -1
            else:
                side = 1

            pieceChessType = self.stringToPiece[piece.lower()]
            table = mappedPieces[piece.lower()]
            locationScore += table[transformIndex(index)] * side
            material += self.pieces[pieceChessType] * side

            
        score = material*3 + locationScore/10 + kingDist*6
        # score = material*3 + locationScore/10 + kingDist*0.5

        if state.is_check():
            if state.turn == self.color:
                # bot is in check
                score -= 1000
            else:
                # opponent in check
                score += 50
        elif len(list(state.legal_moves)) == 0:
            if state.turn == self.color:
                # bot is in checkmate
                score = float('-inf')
            else:
                # opponent in checkmate
                score = float('inf')
        score /= self.pieces[chess.PAWN]
        self.transpositionTable[hashed] = score
        return score
    
