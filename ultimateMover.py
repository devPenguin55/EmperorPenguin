import random as r
import chess
import time as t


class Player:
    def __init__(self, board, color, t, experiments=not True):
        self.color = color # doesn't matter, gets overwritten by board.turn when move
        self.experiments = experiments
        self.justOutOfBook = False
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
            
            if self.experiments == False:
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
                        if side == 1:
                            locationScore += table[index]
                # print(material, locationScore)

            else:
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
                    if side == 1:
                        locationScore += table[transformIndex(index)]
                    material += self.pieces[pieceChessType] * side
                # print(material, locationScore)
            
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

    # def flattenBoard(self, board):
    #     def makeMatrix(board):  # type(board) == chess.Board()
    #         '''
    #         https://stackoverflow.com/questions/55876336/is-there-a-way-to-convert-a-python-chess-board-into-a-list-of-integers
    #         this is where this function came from
    #         '''
    #         pgn = board.epd()
    #         foo = []  # Final board
    #         pieces = pgn.split(" ", 1)[0]
    #         rows = pieces.split("/")
    #         for row in rows:
    #             foo2 = []  # This is the row I make
    #             for thing in row:
    #                 if thing.isdigit():
    #                     for i in range(0, int(thing)):
    #                         foo2.append('.')
    #                 else:
    #                     foo2.append(thing)
    #             foo.append(foo2)
    #         return foo

    #     boardAsList = makeMatrix(board)
    #     x = []
    #     for row in boardAsList:
    #         x += row
    #     boardAsList = x
    #     return boardAsList

    def move(self, board:chess.Board, timeLeft):
        self.color = board.turn
        print(self.color)
        import time as t
        # handle book moves
        move = self.bookMove(board)
        if move:
            print(f'Book move - {move}')
            self.justOutOfBook = True
            return move

        def orderMoves(state:chess.Board, moves, agent):
            import numpy as np
            statePromoted = state.promoted
            sortedMoves = np.empty((0, 2))

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
                
                sortedMoves = np.append(sortedMoves, np.array([[move, moveEstimate]]), axis=0)

                state.pop()
            
            # if state.turn == self.color:
            #     sortedMoves = sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
            # else:
            #     sortedMoves = sortedMoves[sortedMoves[:,1].argsort()][:,0]
            sortedMoves = sortedMoves[sortedMoves[:,1].argsort()[::-1]][:,0]
            return sortedMoves
            

        global positionsEvaluated
        positionsEvaluated = 0

        def quiesce(state:chess.Board, a, b, depth):
            standPat = self.evaluationFunction(state)
            if depth == 2: # search up till both sides do their captures
                return standPat

            if standPat >= b:
                return b
            if standPat > a:
                a = standPat

            captures = []
            for move in state.legal_moves:
                if state.is_capture(move):
                    captures.append(move)
            for capture in captures:
                state.push(capture)
                val = -quiesce(state, -b, -a, depth + 1)
                state.pop()

                if val >= b:
                    return b
                if val > a:
                    a = val
            return a
        
        def minimax(state:chess.Board, depth, agent, a, b, startTime, maxTime):
            if t.time()-startTime > maxTime:
                # if we have exceeded the time given, raise an error
                1/0
            

            global positionsEvaluated

            if depth == 0 or state.is_game_over():
                positionsEvaluated += 1
                # if self.experiments:
                #     return quiesce(state, a, b, 0)
                # else:
                #     return self.evaluationFunction(state)
                return self.evaluationFunction(state)

            if agent == self.color:
                # null move code
                if self.experiments and depth > 1:
                    nullMove = chess.Move.null()

                    state.push(nullMove)

                    # run a shallow depth search to see how good it was? instead of an evaluation on it           
                    nullMoveEstimate = minimax(state, depth-1, not agent, -b, -b+1, startTime, maxTime)                
                    state.pop() 

                    if nullMoveEstimate >= b:
                        return b
                    
                best = float('-inf')
                legalMoves = state.legal_moves

                if self.experiments:
                    legalMoves = orderMoves(state, legalMoves, agent)

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
                # null move code
                if self.experiments and depth > 1:
                    nullMove = chess.Move.null()

                    state.push(nullMove)

                    # run a shallow depth search to see how good it was? instead of an evaluation on it           
                    nullMoveEstimate = minimax(state, depth-1, not agent, -b, -b+1, startTime, maxTime)                
                    state.pop() 

                    if nullMoveEstimate >= b:
                        return b
                    
                best = float('inf') 
                legalMoves = state.legal_moves

                if self.experiments:
                    legalMoves = orderMoves(state, legalMoves, agent)

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

        def searchFromRoot(wantedDepth, st, endTime, boardCopy:chess.Board):
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

            return bestMove, bestVal
        
        def evalMove(args):
            func, state, depth, agent, a, b, startTime, maxTime = args
            return func(state, depth, agent, a, b, startTime, maxTime)
        def searchFromRootWithPool(wantedDepth, st, endTime, boardCopy:chess.Board):
            print(__name__)
            if __name__ == '__main__':
                args = []
                for move in boardCopy.legal_moves:
                    boardCopy.push(move)
                    args.append((minimax, boardCopy.copy(), wantedDepth-1, not self.color, float('-inf'), float('inf'), st, endTime))
                    boardCopy.pop()
                
                import multiprocessing
                
                # from os import cpu_count
                with multiprocessing.Pool(1) as pool:
                    pool.map(evalMove, args)
                quit()
            
        

        def iterativeDeepening(timeAllocation, depthLimit):
            curDepth = 1
            startedTime = t.time()
            boardCopy = board.copy()
            bestMoveFound = None
            lastTime = t.time()
            while t.time()-startedTime < timeAllocation and curDepth <= depthLimit:
                try:
                    # if self.experiments == False:
                    #     bestMoveFound, curVal = searchFromRoot(
                    #         curDepth, startedTime, timeAllocation, boardCopy)
                    # else:
                    #     bestMoveFound, curVal = searchFromRootWithPool(
                    #         curDepth, startedTime, timeAllocation, boardCopy)
                    bestMoveFound, curVal = searchFromRoot(
                                curDepth, startedTime, timeAllocation, boardCopy)
                    print(
                        f'   |___ Iterative Deepening - depth {curDepth}, {bestMoveFound}, {curVal}, took {t.time()-lastTime}s, cum {t.time()-startedTime}s')
                    lastTime = t.time()
                    curDepth += 1
                except ZeroDivisionError:
                    # when the zero division error traces down to here
                    # we have exceeded time limit, so halt the search where it is, and break out of loop
                    break

            return bestMoveFound


        def timeFromState(state):
            baseTime =  1.5 # 1.50
            timeIncrement = 0.50
            # just from book moves is more time
            # doing bad is more time
            stableness = self.evaluationFunction(state)
            if stableness < 0:
                # bot doing bad
                baseTime += timeIncrement
            if self.justOutOfBook:
                self.justOutOfBook = False
                baseTime += timeIncrement

            return baseTime


        startTime = t.time()
        print('Latest Version')
        # given that we have x time left, allocate at most x secs, and have at most y depth
        timeToUse = timeFromState(board)
        # timeToUse = 20 # for when playing a human

        bestMove = iterativeDeepening(timeAllocation=timeToUse, depthLimit=50)  
        print(
            f'        |___ {bestMove}, took {"{:,}".format(t.time()-startTime)} secs, {"{:,}".format(positionsEvaluated)} positions evaluated')
        print("{:,}".format(len(self.transpositionTable)))
        print()
        

        # once done iterative deepening, last move is still valid? like the canceled search is still okay

        return bestMove
    
if __name__ == '__main__':
    board = chess.Board(fen='''
    r1bqkbnr/1pp2ppp/p1n1p3/1Q6/2p1P3/2N2N2/PP3PPP/R1B1KB1R w KQkq - 0 8''')
    up = chess.WHITE

    Player(board, up, 10000, experiments=True).move(board, 10000)