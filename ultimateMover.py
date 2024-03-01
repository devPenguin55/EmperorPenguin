import random as r
import chess
import time as t


class Player:
    def __init__(self, board, color, t, moveOrdering=True):
        self.color = color # doesn't matter, gets overwritten by board.trun when move
        self.moveOrdering = moveOrdering
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
            chess.KING: 200,
            chess.QUEEN: 90,
            chess.ROOK: 50,
            chess.BISHOP: 30,
            chess.KNIGHT: 30,
            chess.PAWN: 10,
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

    def evaluationFunction(self, state:chess.Board):
        from chess import polyglot
        hashed = polyglot.zobrist_hash(state)

        if hashed in self.transpositionTable:
            return self.transpositionTable[hashed]
        else:
            oppPieces = 7 # REMOVE THIS LINE WHEN BELOW FIXED

            # FIX THIS -> how to find opp pieces now?
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
            material = 0
            locationScore = 0
            
            for square in chess.SQUARES:
                piece = state.piece_at(square)
                if piece is not None:
                    pieceSymbol = piece.symbol()
                    index = 8 * (7 - chess.square_rank(square)) + chess.square_file(square)

                    if self.color == True and pieceSymbol == pieceSymbol.lower():
                        side = -1
                    elif self.color == False and pieceSymbol == pieceSymbol.upper():
                        side = -1
                    else:
                        side = 1


                    pieceChessType = self.stringToPiece[pieceSymbol.lower()]
                    material += self.pieces[pieceChessType] * side

                    table = mappedPieces[pieceSymbol.lower()]
                    locationScore += table[index]

            
            score = material*3 + locationScore/10 + kingDist*6
            # score = material*3 + locationScore/10 + kingDist*0.5

            if state.is_check():
                if state.turn == self.color:
                    # bot is in check
                    score -= 1000
                else:
                    # opponent in check
                    score += 50
            elif state.is_checkmate():
                if state.turn == self.color:
                    # bot is in checkmate
                    score = float('-inf')
                else:
                    # opponent in checkmate
                    score = float('inf')

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

    def move(self, board:chess.Board, timeLeft):
        self.color = board.turn
        print(self.color)
        import time as t
        # handle book moves
        move = self.bookMove(board)
        if move:
            print(f'Book move - {move}')
            return move

        def orderMoves(state:chess.Board, moves, agent):
            statePromoted = state.promoted
            # moveScores = []
            
            from collections import deque
            new = deque()

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
                if state.is_checkmate():
                    if state.turn == agent:
                        moveEstimate -= 1000
                    else:
                        moveEstimate += 1000
                if state.is_check():
                    if state.turn == agent:
                        moveEstimate -= 250
                    else:
                        moveEstimate += 250
                

                # moveScores.append(moveEstimate)
                if moveEstimate > 0:
                    new.appendleft(move)
                else:
                    new.append(move)
                state.pop()

            # def insertionSort(moveScores, moves):
            #     n = len(moveScores)
            #     for i in range(1, n):
            #         key = moveScores[i]
            #         key2 = moves[i]
            #         j = i - 1
            #         while j >= 0 and moveScores[j] < key:
            #             moveScores[j + 1] = moveScores[j]
            #             moves[j + 1] = moves[j]
            #             j -= 1
            #         moveScores[j + 1] = key
            #         moves[j + 1] = key2
            #     return moves


            # sortedMoves = insertionSort(moveScores, list(moves))
            # return sortedMoves

            return new
            

        global positionsEvaluated
        positionsEvaluated = 0

        def minimax(state:chess.Board, depth, agent, a, b, startTime, maxTime):
            if t.time()-startTime > maxTime:
                # if we have exceeded the time given, raise an error
                1/0
            global positionsEvaluated

            if depth == 0 or state.is_game_over():
                positionsEvaluated += 1
                return self.evaluationFunction(state)

            if agent == self.color:
                best = float('-inf')
                legalMoves = state.legal_moves
                # if self.moveOrdering:
                #     legalMoves = orderMoves(state, legalMoves, agent)
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
                    
                    # null move code
                    if self.moveOrdering and depth > 1:

                        nullMove = chess.Move.null()

                        state.push(nullMove)
                        
                        nullMoveEstimate = 0
                        if state.is_stalemate():
                            nullMoveEstimate -= 40
                        if state.is_checkmate():
                            if state.turn == (not agent):
                                nullMoveEstimate -= 1000
                            else:
                                nullMoveEstimate += 1000
                        if state.is_check():
                            if state.turn == (not agent):
                                nullMoveEstimate -= 250
                            else:
                                nullMoveEstimate += 250
                        # nullMoveEstimate = minimax(state, depth-1, not agent,
                        # a, b, startTime, maxTime)
                        state.pop()

                        if nullMoveEstimate >= b:
                            # state.pop()
                            return nullMoveEstimate
            else:
                best = float('inf') 
                legalMoves = state.legal_moves
                # if self.moveOrdering:
                #     legalMoves = orderMoves(state, legalMoves, agent)
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

                    # null move code
                    if self.moveOrdering and depth > 1:
                        nullMove = chess.Move.null()

                        state.push(nullMove)
                        
                        nullMoveEstimate = 0
                        if state.is_stalemate():
                            nullMoveEstimate -= 40
                        if state.is_checkmate():
                            if state.turn == (not agent):
                                nullMoveEstimate -= 1000
                            else:
                                nullMoveEstimate += 1000
                        if state.is_check():
                            if state.turn == (not agent):
                                nullMoveEstimate -= 250
                            else:
                                nullMoveEstimate += 250

                        # nullMoveEstimate = minimax(state, depth-1, not agent,
                                        #    a, b, startTime, maxTime)

                        state.pop()

                        if nullMoveEstimate <= a:
                            # state.pop()
                            return nullMoveEstimate
                    

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
                val = minimax(boardCopy, wantedDepth-1, not self.color, a, b, st, endTime)
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
        bestMove = iterativeDeepening(timeAllocation=5, depthLimit=50)

        print(
            f'        |___ {bestMove}, took {"{:,}".format(t.time()-startTime)} secs, {"{:,}".format(positionsEvaluated)} positions evaluated')
        print()

        # once done iterative deepening, last move is still valid? like the canceled search is still okay

        return bestMove
