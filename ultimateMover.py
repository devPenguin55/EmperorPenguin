import random as r
import chess
import time as t
import multiprocessing as mp
from multiprocessing import Manager
from tqdm import tqdm
from copy import deepcopy

from evaluation import evaluationFunction
from moveOrderer import orderMoves
from transpositionTable import TT, entry
from betterBoard import BetterBoard
import boardAndPieceEvaluationHelpers
import settings

chess.Board.__hash__ = chess.polyglot.zobrist_hash

def mpMinimax(param):
    self, tt, killerMoves, boardCopy, move, wantedDepth, color, a, b, st, endTime, iterativeDeepeningDepth = param
    boardCopy.push(move)

    value, pv = self.minimax(boardCopy, wantedDepth, color, a, b, st, endTime, tt, killerMoves, iterativeDeepeningDepth, self.PVN)
    pv = [(move, wantedDepth+1)] + pv
    boardCopy.pop()

    return (move, value, self.positionsEvaluated, self.transpositionMatches, self.gameOverStatesFound, self.prunes, pv)


class Player:
    def __init__(self, board, color, t):
        self.board = BetterBoard(board, color)
        self.color = color

        self.justOutOfBook = False
        self.bookMovesPlayed = 0

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

        if self.color == chess.BLACK:
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
        self.transpositionTable = TT({})
        self.timeToThink = t/40
        self.timeToThink = 2 # 5 IS ONLY FOR HUMAN GAME - REMOVE IF NOT DOING A HUMAN GAME
        
        self.positionsEvaluated = 0
        self.prunes = 0
        self.transpositionMatches = 0

        self.EXACT = 1
        self.LOWERBOUND = 2
        self.UPPERBOUND = 3
        self.CHECKMATE = 9999999

        self.PVN = []
        self.CN = []
        self.AN = []

        self.killerMoves = []

        self.minDepth = settings.minDepth

    # def bookMove(self, state:chess.Board):
    #     with chess.polyglot.open_reader("bookMoves.bin") as reader:
    #         entries = list(reader.find_all(state))
    #         if entries:
    #             gottenMove = r.choice(entries).move # for injecting some variety to its openings
    #             self.bookMovesPlayed += 1
    #             return gottenMove 
    #         else:
    #             return False

    def bookMove(self, state:chess.Board):
        with chess.polyglot.open_reader("bookMoves.bin") as reader:
            entries = list(reader.find_all(state))
            if entries:
                gottenMove = r.choice(entries).move # for injecting some variety to its openings
                self.bookMovesPlayed += 1
                return gottenMove 
            else:
                return False

    def quiesce(self, state:BetterBoard, agent, a, b, depth):
        evaluation = evaluationFunction(self, state, forceAgent=agent)
        if evaluation >= b:
            return b
        
        # if depth == 4:
        #     return evaluation
        
        a = max(a, evaluation)

        captureMoves = [move for move in state.moduleBoard.legal_moves if state.moduleBoard.is_capture(move)]
        for move in captureMoves:
            state.push(move)
            evaluation = -self.quiesce(state, not agent, -b, -a, depth+1)
            state.pop()

            if evaluation >= b:
                return b
            a = max(a, evaluation)
        return a
    
    def minimax(self, state:BetterBoard, depth, agent, a, b, startTime, maxTime, tt, killerMoves, iterativeDeepeningDepth, pv):
        if t.time()-startTime > maxTime and iterativeDeepeningDepth >= self.minDepth: # iterativeDeepeningDepth 0, 1, 2, 3 means depth 1, 2, 3, 4
            # if we have exceeded the time given, raise an error to end all minimax processes
            # only may happen if at least 1 depth has been searched
            1/0

        # do not return pv at terminal / leaf nodes      
        origAlpha = a

        ttEntry = self.transpositionTable.lookup(state.moduleBoard)
        if ttEntry is not None and ttEntry.depth == depth:
            # print(depth, ttEntry.depth)
            # ttEntry.depth <= depth because a depth closer to 0 is a far deeper depth than one higher
            # so a lower depth means that it has been searched more deeply
            self.transpositionMatches += 1
            if ttEntry.flag == self.EXACT:
                # exact value of the state
                return ttEntry.value, []
            elif ttEntry.flag == self.LOWERBOUND:
                # value could be too low, make sure to not prune values lower than this
                a = max(a, ttEntry.value)
            elif ttEntry.flag == self.UPPERBOUND:
                # value could be too high, make sure to not prune values higher than this
                b = min(b, ttEntry.value)

            # our best move is so good that the opponent will never take it, so prune it!
            if a >= b:
                return ttEntry.value, []
            
            windowEstimate = ttEntry.value
        else:
            windowEstimate = None


        if depth == 0 or state.moduleBoard.is_game_over():
            if state.moduleBoard.is_game_over():
                self.gameOverStatesFound += 1
            self.positionsEvaluated += 1

            # if settings.quiesce:
            #     result = -self.quiesce(state, agent, a, b, 0)
            #     return result, []
            # else:
                # result = evaluationFunction(self, state)
                # tt.store(state.moduleBoard, self.EXACT, depth, result)
                    
                # return result, []

            result = evaluationFunction(self, state)
            # tt.store(state.moduleBoard, self.EXACT, depth, result)
            self.transpositionTable.store(state.moduleBoard, self.EXACT, depth, result)
                    
            return result, []
            
        aspirationLowerBound = -1
        aspirationUpperBound = 1
        aspirationRetryAttempts = 0
        aspirationRetryAttemptLimit = 3
        origPv = pv.copy()
        while True:
            if agent == self.color:                    
                best = float('-inf')
                if settings.moveOrdering:
                    # legalMoves = orderMoves(self, state, state.moduleBoard.legal_moves, agent, depth, pv, tt, killerMoves)
                    legalMoves = orderMoves(self, state, state.moduleBoard.legal_moves, agent, depth, pv, self.transpositionTable, self.killerMoves)
                else:
                    legalMoves = state.moduleBoard.legal_moves

                if windowEstimate:
                    a = windowEstimate + aspirationLowerBound
                    b = windowEstimate + aspirationUpperBound

                # if depth == 1:
                #     legalMoves = [move for move in legalMoves if state.moduleBoard.is_capture(move)]

                for move in legalMoves:

                    state.push(move)
                    # val, childPv = self.minimax(state, depth-1, not agent, a, b, startTime, maxTime, tt, killerMoves, iterativeDeepeningDepth, pv)
                    val, childPv = self.minimax(state, depth-1, not agent, a, b, startTime, maxTime, self.transpositionTable, self.killerMoves, iterativeDeepeningDepth, pv)
                    state.pop()

                    if len(childPv) > 1:
                        prevMoveTo = childPv[0][0].to_square
                        for subMove in childPv[1:]:
                            if subMove[0].to_square == prevMoveTo:
                                val = float("-inf")
                            prevMoveTo = subMove[0].to_square

                    if val > best:
                        best = val
                        pv = [(move, depth)] + childPv    
                        # print(f'Depth {depth} pv {pv}')
                    a = max(a, val)
                    
                    if b <= a:
                        self.prunes += 1
                        # killerMoves.append(move)
                        self.killerMoves.append(move)
                        return best, []
            else:
                best = float('inf') 
                if settings.moveOrdering:
                    # legalMoves = orderMoves(self, state, state.moduleBoard.legal_moves, agent, depth, pv, tt, killerMoves)
                    legalMoves = orderMoves(self, state, state.moduleBoard.legal_moves, agent, depth, pv, self.transpositionTable, self.killerMoves)
                else:
                    legalMoves = state.moduleBoard.legal_moves

                if windowEstimate:
                    a = windowEstimate + aspirationLowerBound
                    b = windowEstimate + aspirationUpperBound

                # if depth == 1:
                #     legalMoves = [move for move in legalMoves if state.moduleBoard.is_capture(move)]

                for move in legalMoves:

                    state.push(move)
                    # val, childPv = self.minimax(state, depth-1, not agent, a, b, startTime, maxTime, tt, killerMoves, iterativeDeepeningDepth, pv)
                    val, childPv = self.minimax(state, depth-1, not agent, a, b, startTime, maxTime, self.transpositionTable, self.killerMoves, iterativeDeepeningDepth, pv)
                    state.pop()

                    if len(childPv) > 1:
                        prevMoveTo = childPv[0][0].to_square
                        for subMove in childPv[1:]:
                            if subMove[0].to_square == prevMoveTo:
                                val = float("inf")
                            prevMoveTo = subMove[0].to_square

                    if val < best:
                        best = val
                        pv = [(move, depth)] + childPv
                        # print(f'Depth {depth} pv {pv}')

                    b = min(b, val)

                    if b <= a:
                        self.prunes += 1
                        # killerMoves.append(move)
                        self.killerMoves.append(move)
                        return best, []     
            if windowEstimate:
                if best < a:
                    aspirationLowerBound -= 1

                    aspirationRetryAttempts += 1
                    print(f'-------------------------  window failed low with {aspirationRetryAttempts} / {aspirationRetryAttemptLimit} attempts -------------------------')
                    pv = origPv.copy()
                elif best > b:
                    aspirationUpperBound += 1

                    aspirationRetryAttempts += 1
                    print(f'-------------------------  window failed high with {aspirationRetryAttempts} / {aspirationRetryAttemptLimit} attempts  -------------------------')
                    pv = origPv.copy()
                else:
                    break

                if aspirationRetryAttempts >= aspirationRetryAttemptLimit:
                    # fall back to full width search if limits are not working
                    a = float('-inf')
                    b = float('inf')
            else:
                break
            

        if best <= origAlpha:
            flag = self.UPPERBOUND
        elif best >= b:
            flag = self.LOWERBOUND
        else:
            flag = self.EXACT 
        # tt.store(state.moduleBoard, flag, depth, best)  
        self.transpositionTable.store(state.moduleBoard, flag, depth, best)  

        

        return best, pv
     
    def move(self, givenBoard:chess.Board, timeLeft):
        self.board.update(givenBoard.copy())
        self.availableTime = timeLeft

        self.board.setColor(givenBoard.turn)
        self.color = self.board.color

        if self.color == chess.WHITE:
            print(f'Bot as white')
        else:
            print(f'Bot as black')
        
        # handle book moves
        move = self.bookMove(self.board.moduleBoard)
        if move:
            print(f'Book move - {move}')
            self.board.push(move)
            self.justOutOfBook = True
            return move
        

        self.positionsEvaluated = 0
        

        # ply x
        # meaning it does 2 moves ahead - one for white, one for black
        # do 2*x to get the full depth look ahead

        def searchFromRootMinimax(wantedDepth, st, endTime, boardCopy:BetterBoard, iterativeDeepeningDepth):
            global positionsEvaluated
            bestVal = float('-inf')
            bestMove = None
            a, b = float('-inf'), float('inf')
            orderedMoves = orderMoves(self, boardCopy, boardCopy.moduleBoard.legal_moves, self.color, wantedDepth, self.PVN, self.transpositionTable, self.killerMoves)

            for move in orderedMoves:
                boardCopy.push(move)
                val, pv = self.minimax(boardCopy, wantedDepth-1, not self.color, a, b, st, endTime, self.transpositionTable, self.killerMoves, iterativeDeepeningDepth, []) # get values
                boardCopy.pop()
                if val > bestVal:
                    bestVal = val
                    bestMove = move
                    self.PVN = [(move, wantedDepth)] + pv
                a = max(a, val)

                if b <= a:
                    break
            # print(f'   |___ {len(orderedMoves)} legal moves to search')
            # with Manager() as manager:
            #     sharedDict = manager.dict()
            #     tt = TT(sharedDict)
            #     killerMoves = manager.list(self.killerMoves)
            #     with mp.Pool(min(mp.cpu_count(), len(orderedMoves))) as pool:
            #         results = pool.map(mpMinimax, [(self, tt, killerMoves, boardCopy, move, wantedDepth-1, not self.color, a, b, st, endTime, iterativeDeepeningDepth) for move in orderedMoves])
            #     self.transpositionTable = tt.copy()
            #     self.killerMoves = deepcopy(killerMoves)
            # results.sort(key=lambda x: x[1])
            # bestMove, bestVal, _, _, _, _, self.PVN = results[-1]

            # self.positionsEvaluated   = sum([i for _, _, i, _, _, _, _ in results])
            # self.transpositionMatches = sum([i for _, _, _, i, _, _, _ in results])
            # self.gameOverStatesFound  = sum([i for _, _, _, _, i, _, _ in results])
            # self.prunes  = sum([i for _, _, _, _, _, i, _ in results])
            return bestMove, bestVal
        

        def iterativeDeepening(timeAllocation, depthLimit):
            startedTime = t.time()
            boardCopy = self.board.copy()
            bestMoveFound = None
            lastTime = t.time()
            iterativeDeepeningDepth = 0
            curDepth = 1
            self.PVN.clear()
            self.transpositionTable.clear()
            self.killerMoves.clear()

            # make sure it does not terminate until it hits the right depth, but it should still keep going after hitting that
            while (t.time()-startedTime < timeAllocation and curDepth <= depthLimit) or (iterativeDeepeningDepth <= self.minDepth):
                try:
                    self.transpositionMatches = 0
                    self.gameOverStatesFound = 0
                    self.prunes = 0
                    

                    bestMoveFound, curVal = searchFromRootMinimax(curDepth, startedTime, timeAllocation, boardCopy, iterativeDeepeningDepth)
                    
                    if curVal == -self.CHECKMATE:
                        curVal = f'losing mate seen at depth {curDepth}'
                    elif curVal == self.CHECKMATE:
                        curVal = f'winning mate seen at depth {curDepth}'
                    print(
                        f'       |___ Iterative Deepening - depth {curDepth}, PV -> {[(i[0].uci(),i[1]) for i in self.PVN]}, move {bestMoveFound}, eval {curVal}, gameOverNodes {self.gameOverStatesFound}, prunes {self.prunes}, pos {self.positionsEvaluated}, tt size {len(self.transpositionTable)}, tt matches {self.transpositionMatches}, took {round(t.time()-lastTime, 2)}s, cum {round(t.time()-startedTime, 2)}s')
                
                    lastTime = t.time()
                    if curVal == str(curVal):
                        if 'mate seen' in curVal:
                            print(f'Stopped searching at depth {curDepth} because mate was seen')
                            break
                    curDepth += 1
                except ZeroDivisionError:
                    # when the zero division error traces down to here
                    # we have exceeded time limit, so halt the search where it is, and break out of loop
                    break
                iterativeDeepeningDepth += 1
            print(bestMoveFound)
            return bestMoveFound

        
        def timeFromState(state):
            baseTime = self.timeToThink # 1.50 is what its supposed to be. given time/40 -> 60/40 = 1.5
            timeIncrement = self.timeToThink/3  # 1.5/3 = 0.5 
            # just from book moves is more time
            # doing bad is more time
            # stableness = self.quiesce(state, self.color, float('-inf'), float('inf'), -10)
            stableness = evaluationFunction(self, state)
            if stableness < 0:
                # bot doing bad
                baseTime += timeIncrement
            if self.justOutOfBook:
                self.justOutOfBook = False
                baseTime += timeIncrement

            return baseTime, stableness

        startTime = t.time()
        print('Latest Version')
        # given that we have x time left, allocate at most x secs, and have at most y depth
        timeToUse, stableness = timeFromState(self.board)
        # timeToUse = 20
        # self.transpositionTable.clear()
        bestMove = iterativeDeepening(timeAllocation=timeToUse, depthLimit=55)  
        self.board.push(bestMove)

        conversion = {
            self.board.OPENING:'opening',
            self.board.MIDDLEGAME:'middle game',
            self.board.ENDGAME:'end game'
        }

        print(f'        |___ {bestMove}, took {"{:,}".format(t.time()-startTime)} secs, {"{:,}".format(self.positionsEvaluated)} positions evaluated, in {conversion[self.board.phase]}')
        print("{:,}".format(len(self.transpositionTable.table)), 'entries in transposition table')
        if stableness > 0:
            print('Bot thinks it is winning,', 'eval is', stableness)
        elif stableness < 0:
            print('Bot thinks it is losing,', 'eval is', stableness)
        else:
            print('Bot thinks it is even', 'eval is', stableness)
        print()
        

        # once done iterative deepening, last move is still valid? like the canceled search is still okay
        
        return bestMove
    
if __name__ == '__main__':
    board = chess.Board('8/8/r4kP1/5P2/1R3K2/8/8/8 w - - 0 1')
    p1 = Player(board=board, color=chess.WHITE, t=500000)

    modBoard = BetterBoard(board, p1.color)
    print(evaluationFunction(p1, modBoard))
    print(p1.board.phase)
    print(boardAndPieceEvaluationHelpers.phaseOfGame(board=modBoard))
    print(p1.move(board, 1000000))

    import chessAiOldVersion
    print(chessAiOldVersion.Player(board, chess.WHITE, 1000000).move(board, 1000000))