import random as r
import chess
import time as t


class Player:
    
    def __init__(self, board, color, t):
        self.BENCHMARK = True
        self.color = color
        self.pawns = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5, -10,  0,  0, -10, -5,  5,
            5, 10, 10, -20, -20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        self.knights = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20,  0,  0,  0,  0, -20, -40,
            -30,  0, 10, 15, 15, 10,  0, -30,
            -30,  5, 15, 20, 20, 15,  5, -30,
            -30,  0, 15, 20, 20, 15,  0, -30,
            -30,  5, 10, 15, 15, 10,  5, -30,
            -40, -20,  0,  5,  5,  0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50,
        ]
        self.bishops = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  5, 10, 10,  5,  0, -10,
            -10,  5,  5, 10, 10,  5,  5, -10,
            -10,  0, 10, 10, 10, 10,  0, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10,  5,  0,  0,  0,  0,  5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20,
        ]
        self.rooks = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]
        self.queen = [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  5,  5,  5,  5,  0, -10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0, -10,
            -10,  0,  5,  0,  0,  0,  0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ]
        self.kingMiddleGame = [
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            20, 20,  0,  0,  0,  0, 20, 20,
            20, 30, 10,  0,  0, 10, 30, 20
        ]
        self.kingEndGame = [
            -50, -40, -30, -20, -20, -30, -40, -50,
            -30, -20, -10,  0,  0, -10, -20, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -30,  0,  0,  0,  0, -30, -30,
            -50, -30, -30, -30, -30, -30, -30, -50
        ]

        if self.color == False:
            # black will invert the tables
            self.pawns.reverse()
            self.bishops.reverse()
            self.knights.reverse()
            self.queen.reverse()
            self.rooks.reverse()
            self.kingMiddleGame.reverse()
            self.kingEndGame.reverse()

        # read in the respective book move files, read in the lines, then pick a random line
        # it will look like: d4 Nf3 c4 g3 Bg2 Nc3 O-O Re1 e4 d5 exd5 Bf4 Nb5 Qxd8 gxf4 Ng5 Nd6 Kxg2 Kg3 Nxb7\n
        # therefore you must split on the space and remove the last 2 chars
        if self.color == True:
            moves = r.choice(open('whiteBook.txt', "r").readlines())
            self.bookMoves = moves[:-1].split(" ")

            if self.BENCHMARK:
                self.bookMoves = ['d2d4', 'g2g3', 'f1g2', 'g1h3']

            print(' '.join(self.bookMoves) + " //// are whites book moves")
        else:
            moves = r.choice(open('blackBook.txt', "r").readlines())
            self.bookMoves = moves[:-1].split(" ")

            if self.BENCHMARK:
                self.bookMoves = ['d7d5', 'e7e5']

            print(' '.join(self.bookMoves) + " //// are blacks book moves")
        self.bookMoveIndex = 0
        self.pieces = {
                 chess.KING: 20_000,
                 chess.QUEEN: 900,
                 chess.ROOK: 500,
                 chess.BISHOP: 330,
                 chess.KNIGHT: 320,
                 chess.PAWN: 100,
             }
        self.transpositionTable = {}

    
    def evaluationFunction(self, board, color):
        from chess import polyglot
        hashed = polyglot.zobrist_hash(board)
        if hashed in self.transpositionTable:
            return self.transpositionTable[hashed]
        else:
            

            def pieceCount(piece, color):
                # get amt of pieces on the board that are a certain color and type
                return len(board.pieces(piece, color))

            material = 0
            for piece in self.pieces:
                # in chess module, white is True, black is False
                # therefore, to get the next agent, just do not agent
                # True -> False, False -> True
                material += self.pieces[piece] * (pieceCount(piece, color) -
                                             pieceCount(piece, not color))

            m = board.piece_map()
            flattenedBoard = self.flattenBoard(board)

            oppPieces = 0
            for i in flattenedBoard:
                # if the piece is black and u are white, then 
                # negate ur color to black, and it with 
                if i != '.':
                    if self.color == True and i == i.lower():
                        # u are white, piece is black
                        oppPieces += 1
                    elif self.color == False and i == i.upper():
                        # u are black and piece is white
                        oppPieces += 1

            if oppPieces > 6:
                kingDist = 0
                kingGame = self.kingMiddleGame
            else:
                # move king close to other king to get checkmate in endgame
                kingDist = 500*(1/(chess.square_distance(board.king(self.color), board.king(not self.color))))
                kingGame = self.kingEndGame

            mappedPieces = {
                'p': self.pawns,
                'n': self.knights,
                'b': self.bishops,
                'r': self.rooks,
                'q': self.queen,
                'k': kingGame
            }

            pieceIndices = [c for c in m]
            locationScore = 0
            for index in pieceIndices:
                currentPiece = flattenedBoard[index].lower()
                if currentPiece != '.':
                    table = mappedPieces[currentPiece]
                    locationScore += table[index]

            score = material*1.2 + locationScore*2 + kingDist*5
            self.transpositionTable[hashed] = score
            return score

    def flattenBoard(self, board):
        def makeMatrix(board):  # type(board) == chess.Board()
            '''
            https://stackoverflow.com/questions/55876336/is-there-a-way-to-convert-a-python-chess-board-into-a-list-of-integers
            this is where this function came from
            '''
            pgn = board.epd()
            foo = []  # Final board
            pieces = pgn.split(" ", 1)[0]
            rows = pieces.split("/")
            for row in rows:
                foo2 = []  # This is the row I make
                for thing in row:
                    if thing.isdigit():
                        for i in range(0, int(thing)):
                            foo2.append('.')
                    else:
                        foo2.append(thing)
                foo.append(foo2)
            return foo

        boardAsList = makeMatrix(board)
        x = []
        for row in boardAsList:
            x += row
        boardAsList = x
        return boardAsList

    def move(self, board, timeLeft):
        import time as t

        # handle book moves
        if self.bookMoveIndex < len(self.bookMoves) and self.bookMoveIndex < 7:
            bookMove = self.bookMoves[self.bookMoveIndex]
            self.bookMoveIndex += 1
            return chess.Move.from_uci(bookMove)


        global positionsEvaluated
        positionsEvaluated = 0

        def minimax(state, depth, agent):
            global positionsEvaluated
            if depth == 0 or state.is_game_over():
                positionsEvaluated += 1
                return self.evaluationFunction(board, agent)
            if agent == self.color:
                best = float('-inf')
                legalMoves = list(state.legal_moves)
                for move in legalMoves:
                    positionsEvaluated += 1
                    state.push(move)
                    val = minimax(state, depth-1, not agent)
                    if val > best:
                        best = val
                    state.pop()
            else:
                best = float('inf')
                legalMoves = list(state.legal_moves)
                for move in legalMoves:
                    positionsEvaluated += 1
                    state.push(move)
                    val = minimax(state, depth-1, not agent)
                    if val < best:
                        best = val
                    state.pop()
            return best
        

        startTime = t.time()
        
        wantedDepth = 4
        print(f'searching at depth {wantedDepth}')
        # ply x
        # meaning it does 2 moves ahead - one for white, one for black
        # do 2*x to get the full depth look ahead

        best = float('-inf')

        legal = list(board.legal_moves)

        bestMove = legal[0]
        for move in legal:
            board.push(move)
            val = minimax(board, wantedDepth-1, not self.color)
            if val > best:
                best = val
                bestMove = move
            board.pop()

        print(f'-------> {t.time()-startTime} secs, {positionsEvaluated} positions evaluated')
        print()
        return bestMove
        