import random as r
import chess
import time as t
import requests
import json

from evaluation import evaluationFunction
from moveOrderer import orderMoves

class Player:
    def __init__(self, board, color, t, experiments=True):
        self.color = board.turn
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
        self.transpositionTable = {}
        self.killers = []
        self.availableTime = t

    def bookMove(self, state:chess.Board):
        with chess.polyglot.open_reader("bookMoves.bin") as reader:
            entries = list(reader.find_all(state))
            if entries:
                return r.choice(entries).move # for injecting some variety to its openings
            else:
                return False

    def quiesce(self, state:chess.Board, a, b, depth):
        global positionsEvaluated
        standPat = evaluationFunction(self, state)
        if depth == 4:
            return standPat
        if state.turn == self.color:
            if standPat >= b:
                return b
            if standPat > a:
                a = standPat
        else:
            if standPat <= a:
                return a
            if standPat < b:
                b = standPat
            
        captureMoves = []
        for move in state.legal_moves:
            if state.is_capture(move):
                captureMoves.append(move)

        if not captureMoves:
            return standPat

        for move in orderMoves(self, state, captureMoves, state.turn):

            state.push(move)
            val = self.quiesce(state, a, b, depth + 1)
            positionsEvaluated += 1
            state.pop()

            if state.turn != self.color:
                if val >= b:
                    return b
                if val > a:
                    a = val
            else:
                if val <= a:
                    return a
                if val < b:
                    b = val
                

        if state.turn == self.color:
            return a
        else:
            return b
        
    def minimax(self, state:chess.Board, depth, agent, a, b, startTime, maxTime):
        if t.time()-startTime > maxTime:
            # if we have exceeded the time given, raise an error
            1/0
            

        global positionsEvaluated

        if depth == 0 or state.is_game_over():
            positionsEvaluated += 1
            if self.experiments:
                # res = self.quiesce(state, a, b, 0)
                res = evaluationFunction(self, state)
                return res
            else:
                return evaluationFunction(self, state)
            # return evaluationFunction(self, state)

        if agent == self.color:
            # null move code
            if depth > 1:
                nullMove = chess.Move.null()

                state.push(nullMove)

                positionsEvaluated += 1

                # run a shallow depth search to see how good it was? instead of an evaluation on it           
                nullMoveEstimate = self.minimax(state, depth-1, agent, a, b, startTime, maxTime)                
                state.pop() 

                if nullMoveEstimate >= b:
                    return b
                    
            best = float('-inf')
            legalMoves = orderMoves(self, state, state.legal_moves, agent)
                
            for move in legalMoves:
                positionsEvaluated += 1

                state.push(move)
                val = self.minimax(state, depth-1, not agent,
                              a, b, startTime, maxTime)
                state.pop()

                best = max(best, val)

                a = max(a, val)

                if b <= a:
                    self.killers.append([move, state])
                    break

        else:
            # null move code
            if depth > 1:
                nullMove = chess.Move.null()

                state.push(nullMove)

                positionsEvaluated += 1

                # run a shallow depth search to see how good it was? instead of an evaluation on it           
                nullMoveEstimate = self.minimax(state, depth-1, agent, a, b, startTime, maxTime)                
                state.pop() 

                if nullMoveEstimate >= b:
                    return b
                    
            best = float('inf') 
            legalMoves = orderMoves(self, state, state.legal_moves, agent)
                
            for move in legalMoves:
                positionsEvaluated += 1

                state.push(move)
                val = self.minimax(state, depth-1, not agent,
                              a, b, startTime, maxTime)
                state.pop()

                best = min(best, val)

                b = min(b, val)

                if b <= a:
                    self.killers.append([move, state])
                    break                   

        return best
     
    def move(self, board:chess.Board, timeLeft):
        self.availableTime = timeLeft
        self.color = board.turn
        if self.color == chess.WHITE:
            print(f'Bot as white with experiments set {self.experiments}')
        else:
            print(f'Bot as black with experiments set {self.experiments}')
        # handle book moves
        move = self.bookMove(board)
        if move:
            print(f'Book move - {move}')
            self.justOutOfBook = True
            return move
            

        global positionsEvaluated
        positionsEvaluated = 0


        # ply x
        # meaning it does 2 moves ahead - one for white, one for black
        # do 2*x to get the full depth look ahead

        def searchFromRootMinimax(wantedDepth, st, endTime, boardCopy:chess.Board):
            global positionsEvaluated
            bestVal = float('-inf')
            bestMove = None
            a, b = float('-inf'), float('inf')

            orderedMoves = orderMoves(self, boardCopy, boardCopy.legal_moves, self.color)

            for move in orderedMoves:
                boardCopy.push(move)
                val = self.minimax(boardCopy, wantedDepth-1, not self.color, a, b, st, endTime)
                boardCopy.pop()

                if val > bestVal:
                    bestVal = val
                    bestMove = move
                a = max(a, val)

                if b <= a:
                    self.killers.append([move, boardCopy])
                    break

            return bestMove, bestVal


        def iterativeDeepeningMinimax(timeAllocation, depthLimit):
            curDepth = 1
            startedTime = t.time()
            boardCopy = board.copy()
            bestMoveFound = None
            lastTime = t.time()
            
            self.killers = []

            while t.time()-startedTime < timeAllocation and curDepth <= depthLimit:
                try:
                    bestMoveFound, curVal = searchFromRootMinimax(curDepth, startedTime, timeAllocation, boardCopy)
                    
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
            baseTime = self.availableTime/40 # 1.50 is what its supposed to be. given time/40 -> 60/40 = 1.5
            timeIncrement = baseTime/3  # 1.5/3 = 0.5 
            # just from book moves is more time
            # doing bad is more time
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
        timeToUse, stableness = timeFromState(board)
        # timeToUse = 20 # for when playing a human 

        bestMove = iterativeDeepeningMinimax(timeAllocation=timeToUse, depthLimit=50)  
        print(
            f'        |___ {bestMove}, took {"{:,}".format(t.time()-startTime)} secs, {"{:,}".format(positionsEvaluated)} positions evaluated')
        print("{:,}".format(len(self.transpositionTable)), 'entries in transposition table')
        if stableness > 0:
            print('Bot thinks it is winning,', 'eval is', stableness)
        else:
            print('Bot thinks it is losing,', 'eval is', stableness)
        print()
        

        # once done iterative deepening, last move is still valid? like the canceled search is still okay

        return bestMove
