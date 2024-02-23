import random as r
import chess
import time as t


class Player:
    def __init__(self, board, color, t):
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

        self.pieces = {
            chess.KING: 20_000,
            chess.QUEEN: 900,
            chess.ROOK: 500,
            chess.BISHOP: 330,
            chess.KNIGHT: 320,
            chess.PAWN: 100,
        }
        self.stringToPiece = {
            'p': chess.PAWN,
            'r': chess.ROOK,
            'n': chess.KNIGHT,
            'b': chess.BISHOP,
            'q': chess.QUEEN,
            'k': chess.KING
        }
        self.transpositionTable = {}

    def bookMove(self, state):
        # state -> board
        import chess.polyglot
        with chess.polyglot.open_reader("bookMoves.bin") as reader:
            entries = reader.find_all(state)
            best = False
            for entry in entries:
                best = entry.move
                return best
                # print(entry.move, entry.weight, entry.learn)
            return best

    def evaluationFunction(self, state, agent):
        color = self.color
        # color = not agent
        from chess import polyglot
        hashed = polyglot.zobrist_hash(state)

        if hashed in self.transpositionTable:
            return self.transpositionTable[hashed]
        else:

            def pieceCount(piece, color):
                # get amt of pieces on the board that are a certain color and type
                return len(state.pieces(piece, color))

            material = 0
            for piece in self.pieces:
                # in chess module, white is True, black is False
                # therefore, to get the next agent, just do not agent
                # True -> False, False -> True
                material += self.pieces[piece] * (pieceCount(piece, color) -
                                                  pieceCount(piece, not color))

            m = state.piece_map()
            flattenedBoard = self.flattenBoard(state)

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
                kingDist = 500 * \
                    (1/(chess.square_distance(state.king(self.color),
                     state.king(not self.color))))
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

            unprotectedPieces = []

            for pieceType in chess.PIECE_TYPES:
                for square in state.pieces(pieceType, color):
                    # check if piece attacked by any opponent pieces
                    if state.is_attacked_by(not color, square):
                        # check if no defending pieces on current square
                        if not state.is_attacked_by(color, square):
                            unprotectedPieces.append(self.pieces[pieceType])
            unprotectedPieces = sum(unprotectedPieces)
            # score = material*1.5 + locationScore*1 + kingDist*2 + unprotectedPieces*3
            score = material*1.2 + locationScore*2 + kingDist*5 + unprotectedPieces*2*(1 if agent == color else -1)
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
        move = self.bookMove(board)
        if move:
            print(f'Book move - {move}')
            return move

        def orderMoves(state, moves, agent):
            from chess import polyglot
            hashed = polyglot.zobrist_hash(board)
            if hashed in self.moveOrderTable:
                return self.moveOrderTable[hashed]
            else:
                statePromoted = state.promoted
                moveOrdering = []
                for move in moves:
                    moveEstimate = 0

                    if state.gives_check(move):
                        moveEstimate += 10
                    if state.is_into_check(move):
                        moveEstimate -= 25
                    state.push(move)
                    if state.promoted > statePromoted:
                        moveEstimate += 30
                    if state.is_stalemate():
                        moveEstimate -= 40
                    if state.is_checkmate():
                        if state.turn == agent:
                            moveEstimate -= 1000
                        else:
                            moveEstimate += 1000

                    moveOrdering.append((move, moveEstimate))
                    state.pop()

                if all(score == 0 for _, score in moveOrdering):
                    # if the score of each move was 0, then there's nothing to sort
                    # skip sorting and just return what we have
                    return moves
                moveOrdering.sort(reverse=True, key=lambda x: x[1])
                sortedMoves = [x[0] for x in moveOrdering]
                self.moveOrderTable[hashed] = sortedMoves
                return sortedMoves

        global positionsEvaluated
        positionsEvaluated = 0

        def minimax(state, depth, agent, a, b, startTime, maxTime):
            if t.time()-startTime > maxTime:
                # if we have exceeded the time given, raise an error
                1/0
            global positionsEvaluated

            if depth == 0 or state.is_game_over():
                positionsEvaluated += 1
                return self.evaluationFunction(state, agent)

            if agent == self.color:
                best = float('-inf')
                legalMoves = state.legal_moves
                # legalMoves = orderMoves(state, legalMoves, agent)
                for move in legalMoves:
                    positionsEvaluated += 1

                    state.push(move)
                    val = minimax(state, depth-1, not agent,
                                  a, b, startTime, maxTime)
                    state.pop()

                    best = max(best, val)

                    a = max(a, val)

                    if b <= a:
                        break

            else:
                best = float('inf')
                legalMoves = state.legal_moves
                # legalMoves = orderMoves(state, legalMoves, agent)
                for move in legalMoves:
                    positionsEvaluated += 1

                    state.push(move)
                    val = minimax(state, depth-1, not agent,
                                  a, b, startTime, maxTime)
                    state.pop()

                    best = min(best, val)

                    b = min(b, val)

                    if b <= a:
                        break

            return best

        # ply x
        # meaning it does 2 moves ahead - one for white, one for black
        # do 2*x to get the full depth look ahead

        def searchFromRoot(wantedDepth, st, endTime, boardCopy):
            global positionsEvaluated
            positionsEvaluated = 0
            bestVal = float('-inf')
            bestMove = None

            a, b = float('-inf'), float('inf')

            for move in boardCopy.legal_moves:
                boardCopy.push(move)
                val = minimax(boardCopy, wantedDepth-1,
                              not self.color, a, b, st, endTime)
                boardCopy.pop()

                if val > bestVal:
                    bestVal = val
                    bestMove = move

                a = max(a, val)
                if b <= a:
                    break
            return bestMove

        def iterativeDeepening(timeAllocation, depthLimit):
            curDepth = 1
            startedTime = t.time()
            boardCopy = board.copy()
            bestMoveFound = None
            lastTime = t.time()
            while t.time()-startedTime < timeAllocation and curDepth <= depthLimit:
                try:
                    bestMoveFound = searchFromRoot(
                        curDepth, startedTime, timeAllocation, boardCopy)
                    print(
                        f'   |___ Iterative Deepening - depth {curDepth}, {bestMoveFound}, took {t.time()-lastTime}s, cum {t.time()-startedTime}s')
                    lastTime = t.time()
                    curDepth += 1
                except ZeroDivisionError:
                    # when the zero division error traces down to here
                    # we have exceeded time limit, so halt the search where it is, and break out of loop
                    break

            return bestMoveFound

        startTime = t.time()
        print('Latest Version')
        # given that we have x time left, allocate at most x secs, and have at most y depth
        bestMove = iterativeDeepening(timeAllocation=5, depthLimit=10)

        print(
            f'        |___ {bestMove}, took {"{:,}".format(t.time()-startTime)} secs, {"{:,}".format(positionsEvaluated)} positions evaluated')
        print()

        return bestMove
