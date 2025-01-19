import random as r
import chess
import time as t
import multiprocessing as mp
from multiprocessing import Manager
from tqdm import tqdm
from copy import deepcopy
import numpy as np

from evaluationNEW import evaluationFunction
from moveOrdererNEW import orderMoves
from transpositionTableNEW import TT, entry
from betterBoard import BetterBoard
import boardAndPieceEvaluationHelpers
from syzygyHttpMoveFinder import findBestMoveForEndgame
import settings

chess.Board.__hash__ = chess.polyglot.zobrist_hash


def mpMinimax(param):
    self, tt, killerMoves, boardCopy, move, wantedDepth, color, a, b, st, endTime, iterativeDeepeningDepth = param
    boardCopy.push(move)

    value, pv = self.minimax(boardCopy, wantedDepth, color, a, b, st,
                             endTime, tt, killerMoves, iterativeDeepeningDepth, self.PV)
    pv = [(move, wantedDepth+1)] + pv
    boardCopy.pop()

    return (move, value, self.nodesVisited, self.transpositionMatches, self.gameOverStatesFound, self.prunes, pv)


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

        self.MVV_LVA_TABLE = [
            # victim K, attacker K, Q, R, B, N, P, None
            [0, 0, 0, 0, 0, 0, 0],
            # victim Q, attacker K, Q, R, B, N, P, None
            [50, 51, 52, 53, 54, 55, 0],
            # victim R, attacker K, Q, R, B, N, P, None
            [40, 41, 42, 43, 44, 45, 0],
            # victim B, attacker K, Q, R, B, N, P, None
            [30, 31, 32, 33, 34, 35, 0],
            # victim N, attacker K, Q, R, B, N, P, None
            [20, 21, 22, 23, 24, 25, 0],
            # victim P, attacker K, Q, R, B, N, P, None
            [10, 11, 12, 13, 14, 15, 0],
            # victim None, attacker K, Q, R, B, N, P, None
            [0, 0, 0, 0, 0, 0, 0],
        ]

        self.MVV_LVA_INDEX_CONVERSION = {
            chess.KING: 0,
            chess.QUEEN: 1,
            chess.ROOK: 2,
            chess.BISHOP: 3,
            chess.KNIGHT: 4,
            chess.PAWN: 5,
            None: 6
        }

        self.transpositionTable = TT({})
        self.qSearchTranspositionTable = TT({})
        self.currentAge = 0

        self.timeToThink = t/40
        self.timeToThink = 2  # 5 IS ONLY FOR HUMAN GAME - REMOVE IF NOT DOING A HUMAN GAME

        self.nodesVisited = 0
        self.prunes = 0
        self.transpositionMatches = 0

        self.HASH_EXACT = 1
        self.HASH_ALPHA = 2
        self.HASH_BETA = 3

        self.CHECKMATE = 9_999_999

        self.PV = []

        self.minDepth = settings.minDepth
        self.currentTopDepth = 0

        self.extendNextMoveDepthFromGameOverNodeSeen = False

        self.resetKillers()
        # self.resetHistoryMoves()

    def resetKillers(self):
        self.killers = [[None for _ in range(5)] for _ in range(64)]

    # def resetHistoryMoves(self):
    #     self.historyMoves = [[0 for _ in range(64)] for _ in chess.PIECE_TYPES]

    def bookMove(self, state: chess.Board):
        with chess.polyglot.open_reader("C:\\ChessAi\\UltimateChessAI\\bookMoves.bin") as reader:
            entries = list(reader.find_all(state))
            if entries:
                results = sorted([(i.move, i.weight)
                                 for i in entries], key=lambda x: x[-1], reverse=True)
                results = results[0:min(len(results), 2)]
                return r.choice(results)[0]
            else:
                return False

    def storeKiller(self, move, depth):
        ply = self.currentTopDepth - depth
        if move not in self.killers[ply]:
            self.killers[ply] = [move] + self.killers[ply][:-1]

    def garbageCollection(self):
        return
        evictionsCompleted = 0
        for stateHash in list(self.transpositionTable.table.keys()):
            ttEntry = self.transpositionTable.lookup(
                stateHash, isAlreadyHashed=True)
            if self.currentAge - ttEntry.currentAge > 4:  # evict entries not used for some time
                evictionsCompleted += 1
                del self.transpositionTable.table[stateHash]

        if self.qSearchTranspositionTable:
            for stateHash in list(self.qSearchTranspositionTable.table.keys()):
                ttEntry = self.qSearchTranspositionTable.lookup(
                    stateHash, isAlreadyHashed=True)
                if self.currentAge - ttEntry.currentAge > 4:  # evict entries not used for some time
                    evictionsCompleted += 1
                    del self.qSearchTranspositionTable.table[stateHash]

        print(f'{evictionsCompleted} evictions completed')

    def quiesce(self, state: BetterBoard, agent, a, b, depth):
        self.nodesVisited += 1
        evaluation = evaluationFunction(self, state, forceAgent=agent)
        if evaluation >= b:
            return b

        if depth >= 2:
            return evaluation

        a = max(a, evaluation)

        captureMoves = [
            move for move in state.moduleBoard.legal_moves if state.moduleBoard.is_capture(move)]
        for move in captureMoves:
            state.push(move)
            evaluation = -self.quiesce(state, not agent, -b, -a, depth+1)
            state.pop()

            if evaluation >= b:
                return b
            a = max(a, evaluation)
        return a

    def minimaxQuiesce(self, state: BetterBoard, depth, agent, a, b):
        self.nodesVisited += 1
        # print(len(self.qSearchTranspositionTable))
        agent = state.moduleBoard.turn

        ttEntry = self.qSearchTranspositionTable.lookup(state.moduleBoard)
        if ttEntry is not None and ttEntry.depth >= depth:
            # print(depth, ttEntry.toDict())
            if ttEntry.flag == self.HASH_EXACT:
                return ttEntry.value
            elif ttEntry.flag == self.HASH_ALPHA:
                if ttEntry.value <= a:
                    return a
            elif ttEntry.flag == self.HASH_BETA:
                if ttEntry.value >= b:
                    return b

            if a >= b:
                self.prunes += 1
                return ttEntry.value

        moves = [
            move for move in state.moduleBoard.legal_moves if state.moduleBoard.is_capture(move)]
        hasReachedGameOver = state.moduleBoard.is_game_over(claim_draw=True)

        if not moves or hasReachedGameOver or depth >= 2:
            if hasReachedGameOver:
                self.gameOverStatesFound += 1

            result = evaluationFunction(self, state)
            self.qSearchTranspositionTable.store(
                state.moduleBoard, self.HASH_EXACT, depth, result, None, self.currentAge)
            return result

        best = float('-inf') if agent == self.color else float('inf')
        bestMove = None
        moves = orderMoves(self, state, moves, agent, depth, inQSearch=True)

        flag = self.HASH_ALPHA
        for move in moves:
            state.push(move)
            val = self.minimaxQuiesce(state, depth+1, not agent, a, b)
            state.pop()

            if agent == self.color:
                if val > best:
                    best = val
                    bestMove = move
                    flag = self.HASH_EXACT
                a = max(a, val)
            else:
                if val < best:
                    best = val
                    bestMove = move
                    flag = self.HASH_EXACT
                b = min(b, val)

            if a >= b:
                self.prunes += 1
                self.qSearchTranspositionTable.store(
                    state.moduleBoard, self.HASH_BETA, depth, best, move, self.currentAge)
                return best

        self.qSearchTranspositionTable.store(
            state.moduleBoard, flag, depth, best, bestMove, self.currentAge)
        return best

    def minimax(self, state: BetterBoard, depth, agent, a, b, startTime, maxTime, iterativeDeepeningDepth):
        # iterativeDeepeningDepth 0, 1, 2, 3 means depth 1, 2, 3, 4

        # if t.time()-startTime > maxTime and iterativeDeepeningDepth > self.minDepth and iterativeDeepeningDepth % 2 != 0:
        #     # if we have exceeded the time given, raise an error to end all minimax processes
        #     # only may happen if at least our minimum depth has been searched though
        #     1/0
        if t.time()-startTime > maxTime and iterativeDeepeningDepth > self.minDepth:
            # if we have exceeded the time given, raise an error to end all minimax processes
            # only may happen if at least our minimum depth has been searched though
            1/0

        ttEntry = self.transpositionTable.lookup(state.moduleBoard)
        if ttEntry is not None and ttEntry.depth >= depth:
            self.transpositionMatches += 1
            self.transpositionTable.table[TT.hashState(
                None, state.moduleBoard)].currentAge = self.currentAge
            if ttEntry.flag == self.HASH_EXACT:
                # exact value of the state
                return ttEntry.value
            elif ttEntry.flag == self.HASH_ALPHA:
                if ttEntry.value <= a:
                    return a
            elif ttEntry.flag == self.HASH_BETA:
                if ttEntry.value >= b:
                    return b

            # our best move is so good that the opponent will never take it, so prune it!
            if a >= b:
                self.prunes += 1
                return ttEntry.value

        stateLegalMoves = state.moduleBoard.legal_moves

        self.nodesVisited += 1
        # do not return pv at terminal / leaf nodes or tt fetches
        hasReachedGameOver = state.moduleBoard.is_game_over(claim_draw=True)
        if depth == 0 or hasReachedGameOver:
            if hasReachedGameOver:
                self.gameOverStatesFound += 1

            if settings.quiesce and [move for move in stateLegalMoves if state.moduleBoard.is_capture(move)]:
                result = self.minimaxQuiesce(state, 0, agent, a, b)
                return result
            else:
                # result = evaluationFunction(self, state)
                if hasReachedGameOver:
                    if state.moduleBoard.is_checkmate():
                        if state.moduleBoard.turn == self.color:
                            result = -self.CHECKMATE
                        else:
                            result = self.CHECKMATE
                    else:
                        result = -state.pieces[chess.ROOK]
                else:
                    result = state.material * 10 + state.locationScore/10
                self.transpositionTable.store(
                    state.moduleBoard, self.HASH_EXACT, depth, result, None, self.currentAge)

                return result

        if state.moduleBoard.is_check():
            depth += 1

        # null move pruning
        if depth > 3:
            state.push(chess.Move.null())
            nullEvaluation = self.minimax(
                state, depth-3, not agent, a, b, startTime, maxTime, iterativeDeepeningDepth)
            state.pop()
            if nullEvaluation > b and state.phase != state.ENDGAME:
                return nullEvaluation if agent == self.color else -nullEvaluation

        flag = self.HASH_ALPHA
        bestMove = None
        if agent == self.color:
            best = float('-inf')

            legalMoves = orderMoves(self, state, stateLegalMoves, agent, depth)

            moveNumber = 0
            for move in legalMoves:
                moveNumber += 1
                needsFullSearch = True

                state.push(move)
                if moveNumber >= 3 and depth >= 3 and (not state.moduleBoard.is_capture(move)):
                    reduceDepth = 1
                    val = self.minimax(state, depth-1-reduceDepth, not agent,
                                       a, b, startTime, maxTime, iterativeDeepeningDepth)
                    needsFullSearch = val > a and abs(val) != self.CHECKMATE
                    if needsFullSearch:
                        print('failed lmr')

                if needsFullSearch:
                    val = self.minimax(
                        state, depth-1, not agent, a, b, startTime, maxTime, iterativeDeepeningDepth)

                state.pop()

                if val > best:
                    best = val
                    bestMove = move
                    flag = self.HASH_EXACT
                a = max(a, val)

                if a >= b:
                    self.prunes += 1
                    if not state.moduleBoard.is_capture(move):
                        self.storeKiller(move, depth)
                        
                        # self.historyMoves[state.moduleBoard.piece_type_at(move.from_square)-1][move.to_square] += depth * depth
                    self.transpositionTable.store(
                        state.moduleBoard, self.HASH_BETA, depth, best, bestMove, self.currentAge)
                    return best
        else:
            best = float('inf')
            legalMoves = orderMoves(self, state, stateLegalMoves, agent, depth)

            moveNumber = 0
            for move in legalMoves:
                moveNumber += 1
                needsFullSearch = True

                state.push(move)
                if moveNumber >= 3 and depth >= 3 and (not state.moduleBoard.is_capture(move)):
                    reduceDepth = 1
                    val = self.minimax(state, depth-1-reduceDepth, not agent,
                                       a, b, startTime, maxTime, iterativeDeepeningDepth)
                    needsFullSearch = val < b and abs(val) != self.CHECKMATE

                    if needsFullSearch:
                        print('failed lmr')

                if needsFullSearch:
                    val = self.minimax(
                        state, depth-1, not agent, a, b, startTime, maxTime, iterativeDeepeningDepth)

                state.pop()

                if val < best:
                    best = val
                    bestMove = move
                    flag = self.HASH_EXACT

                b = min(b, val)

                if a >= b:
                    self.prunes += 1
                    if not state.moduleBoard.is_capture(move):
                        self.storeKiller(move, depth)
                        # self.historyMoves[state.moduleBoard.piece_type_at(move.from_square)-1][move.to_square] += depth * depth
                    self.transpositionTable.store(
                        state.moduleBoard, self.HASH_BETA, depth, best, bestMove, self.currentAge)
                    return best

        self.transpositionTable.store(
            state.moduleBoard, flag, depth, best, bestMove, self.currentAge)
        return best

    def move(self, givenBoard: chess.Board, timeLeft):
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

        # ply x
        # meaning it does 2 moves ahead - one for white, one for black
        # do 2*x to get the full depth look ahead

        def searchFromRootMinimax(wantedDepth, st, endTime, boardCopy: BetterBoard, iterativeDeepeningDepth, a, b):
            global nodesVisited
            bestVal = float('-inf')
            bestMove = None
            orderedMoves = orderMoves(
                self, boardCopy, boardCopy.moduleBoard.legal_moves, self.color, wantedDepth)
            
            # assert len(orderedMoves) == len(list(boardCopy.moduleBoard.legal_moves)) # ! if there are bugs on checkmate not found, uncomment this

            self.nodesVisited += 1

            flag = self.HASH_ALPHA
            for move in orderedMoves:
                boardCopy.push(move)
                try:
                    val = self.minimax(boardCopy, wantedDepth-1, not self.color,
                                       a, b, st, endTime, iterativeDeepeningDepth)  # get value
                except ZeroDivisionError:
                    boardCopy.pop()
                    # time is up, return the value to iterative deepening function
                    print(
                        "TIMES UP, next depth's move has come from the new best results right now", bestMove, bestVal)
                    try:
                        boardCopy.push(bestMove)
                        boardCopy.pop()
                    except:
                        bestMove = None
                    if bestVal == float('-inf') or bestVal == float('-inf') or bestMove is None:
                        print('Went with the 1/0 method')
                        1/0
                    else:
                        print('Accepted results')
                        break

                boardCopy.pop()
                if val > bestVal:
                    bestVal = val
                    bestMove = move
                    flag = self.HASH_EXACT
                a = max(a, val)

                if a >= b:
                    self.prunes += 1
                    self.transpositionTable.store(
                        boardCopy.moduleBoard, self.HASH_BETA, wantedDepth, bestVal, bestMove, self.currentAge)
                    break

            self.transpositionTable.store(
                boardCopy.moduleBoard, flag, wantedDepth, bestVal, bestMove, self.currentAge)

            self.PV.clear()
            currentPosition = boardCopy.copy()
            currentPvDepth = wantedDepth
            for _ in range(wantedDepth):
                ttEntry = self.transpositionTable.lookup(
                    currentPosition.moduleBoard)
                if not ttEntry:
                    print('stopped due to position not in table')
                    break

                if ttEntry.bestMove is None:
                    print('stopped due to best move not in entry')
                    break

                if ttEntry.flag != self.HASH_EXACT:
                    print('stopped due to exact store not in table')
                    break

                self.PV.append((ttEntry.bestMove, currentPvDepth))

                temp = currentPosition.copy()
                temp.push(ttEntry.bestMove)
                currentPosition = temp.copy()
                del temp

                currentPvDepth -= 1

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
            # bestMove, bestVal, _, _, _, _, self.PV = results[-1]

            # self.nodesVisited   = sum([i for _, _, i, _, _, _, _ in results])
            # self.transpositionMatches = sum([i for _, _, _, i, _, _, _ in results])
            # self.gameOverStatesFound  = sum([i for _, _, _, _, i, _, _ in results])
            # self.prunes  = sum([i for _, _, _, _, _, i, _ in results])

            return bestMove, bestVal, a, b

        def iterativeDeepening(timeAllocation, depthLimit):
            startedTime = t.time()
            boardCopy = self.board.copy()
            bestMoveFound = None
            curValFound = None
            lastTime = t.time()
            iterativeDeepeningDepth = 0
            curDepth = 1



            self.PV.clear() # ? maybe don't clear the PV for using good moves for the next move? PV gets reset anyways when creating it
            self.transpositionTable.clear()

            self.resetKillers()
            # self.resetHistoryMoves()

            givenBoardAsBetterBoard = BetterBoard(givenBoard, self.color)
            phase = givenBoardAsBetterBoard.phase


            a, b = float('-inf'), float('inf')
            aspirationWindow = 500

            totalNodesVisited = 0
            while ((t.time()-startedTime < timeAllocation and curDepth <= depthLimit) or (iterativeDeepeningDepth <= self.minDepth)) or curDepth % 2 != 0:
                try:
                    self.transpositionMatches = 0
                    self.gameOverStatesFound = 0
                    self.prunes = 0
                    self.nodesVisited = 0

                    self.currentTopDepth = curDepth

                    curBestMoveFound, curVal, _, _ = searchFromRootMinimax(curDepth, startedTime, timeAllocation, boardCopy, iterativeDeepeningDepth, a, b)

                    totalNodesVisited += self.nodesVisited
                    # print(curVal, curBestMoveFound)
                    if (curVal <= a or curVal >= b) and abs(curVal) != self.CHECKMATE:
                        # outside of window, retry search with full-width window
                        print('Retrying search with full-width window   |   old window with cur val ->', a, curVal, b)
                        a, b = float('-inf'), float('inf')
                        continue
                    bestMoveFound = curBestMoveFound
                    curValFound = curVal

                    a = curValFound - aspirationWindow
                    b = curValFound + aspirationWindow

                    if self.gameOverStatesFound != 0:
                        self.extendNextMoveDepthFromGameOverNodeSeen = True

                    if curValFound == -self.CHECKMATE:
                        curValFound = f'losing mate seen at depth {curDepth}'
                    elif curValFound == self.CHECKMATE:
                        curValFound = f'winning mate seen at depth {curDepth}'
                    print(f'       |___ Iterative Deepening - depth {curDepth}, PV -> {[(i[0].uci(), i[1]) for i in self.PV]}, move {bestMoveFound}, eval {curValFound}, gameOverNodes {self.gameOverStatesFound}, prunes {self.prunes}, pos {self.nodesVisited}, tt size {len(self.transpositionTable)}, tt matches {self.transpositionMatches}, took {round(t.time()-lastTime, 2)}s, cum {round(t.time()-startedTime, 2)}s')

                    lastTime = t.time()
                    if curValFound == str(curValFound):
                        if 'mate seen' in curValFound:
                            print(f'Stopped searching at depth {curDepth} because mate was seen')
                            break
                    curDepth += 2
                except ZeroDivisionError:
                    # when the zero division error traces down to here
                    # we have exceeded time limit, so halt the search where it is, and break out of loop

                    break
                iterativeDeepeningDepth += 2
            self.nodesVisited = totalNodesVisited
            return bestMoveFound, curValFound

        def timeFromState(state):
            # 1.50 is what its supposed to be. given time/40 -> 60/40 = 1.5
            baseTime = self.timeToThink
            timeIncrement = self.timeToThink/3  # 1.5/3 = 0.5
            # just from book moves is more time
            # doing bad is more time
            # stableness = self.quiesce(state, self.color, float('-inf'), float('inf'), -10)
            stableness = evaluationFunction(self, state)
            if stableness < 0:
                # bot doing bad
                baseTime += timeIncrement
            if stableness < -3:  # if bot doing really bad, trigger extra depth search -> get out of bad position, do not do unnecessarily
                if not self.extendNextMoveDepthFromGameOverNodeSeen:
                    self.extendNextMoveDepthFromGameOverNodeSeen = True

            if self.justOutOfBook:
                self.justOutOfBook = False
                baseTime += timeIncrement

            return baseTime, stableness

        startTime = t.time()
        print('Latest Version')

        # * for getting best endgame moves with <=7 pieces left
        # ! could be optimized inside of betterBoard when pushing captures
        piecesOnBoard = 0
        for pieceType in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
            for color in [chess.WHITE, chess.BLACK]:
                piecesOnBoard += len(self.board.moduleBoard.pieces(pieceType, color))
        if piecesOnBoard <= 7 and False:
            move = findBestMoveForEndgame(self.board.moduleBoard)
            if move:
                print(f'       |___ Using endgame tablebase, best move -> {
                      move}, took {round(t.time() - startTime, 1)} seconds')
                self.board.push(chess.Move.from_uci(move))
                return chess.Move.from_uci(move)
            else:
                print('ENDGAME TABLEBASE FAILED GETTING A MOVE')

        timeToUse, stableness = timeFromState(self.board)

        triggerNextMoveDepthBack = False
        self.extendNextMoveDepthFromGameOverNodeSeen = False  # ! DO NOT USE
        if self.extendNextMoveDepthFromGameOverNodeSeen:
            self.extendNextMoveDepthFromGameOverNodeSeen = False
            self.minDepth += 1
            settings.minDepth += 1
            triggerNextMoveDepthBack = True

        timeToUse = 20  # for bots 10, humans 20, self-play/testing 5
        # self.transpositionTable.clear()
        # if False:

        bestMove, stableness = iterativeDeepening(
            timeAllocation=timeToUse, depthLimit=55)
        # else:
        # self.transpositionMatches = 0
        # self.gameOverStatesFound = 0
        # self.prunes = 0

        # self.currentTopDepth = 5

        # bestMove, _ = searchFromRootMinimax(
        #     5, startTime, startTime+10000, self.board.copy(), 0)
        self.board.push(bestMove)

        conversion = {
            self.board.OPENING: 'opening',
            self.board.MIDDLEGAME: 'middle game',
            self.board.ENDGAME: 'end game'
        }
        print(f'              |___ {bestMove}, took {"{:,}".format(t.time()-startTime)} secs, {"{:,}".format(self.nodesVisited)} nodes visited, in {
              conversion[self.board.phase]}{', triggering more depth' if self.extendNextMoveDepthFromGameOverNodeSeen else ''}')
        if str(stableness) == stableness:
            print('Bot sees endgame with', stableness)
        else:
            if stableness > 1:
                print('Bot thinks it is winning,', 'eval is', stableness)
            elif stableness < -1:
                print('Bot thinks it is losing,', 'eval is', stableness)
            else:
                print('Bot thinks it is even,', 'eval is', stableness)
        print()

        if triggerNextMoveDepthBack:
            self.minDepth -= 1
            settings.minDepth -= 1
            triggerNextMoveDepthBack = False

        self.garbageCollection()
        self.currentAge += 1
        return bestMove


if __name__ == '__main__':
    # ! add history moves, killer moves possibly implemented incorrectly
    # board = chess.Board('r1bqkbr1/p3pppp/1p3n2/6B1/3N4/2P2P2/PP4PP/R2QKB1R b KQq - 0 11')
    # board = chess.Board('8/8/6n1/4b3/k2P4/4P3/8/4K3 w - - 0 1')
    # board = chess.Board('6q1/k3bq2/q7/Q7/5N2/3B4/1Q6/K7 w - - 2 4')

    board = chess.Board('8/p4pp1/7p/2p5/8/5k2/8/2r1B1K1 b - - 1 69')  # !
    # board = chess.Board('r1bqkbr1/p3pppp/1p3n2/6B1/3N4/2P2P2/PP4PP/R2QKB1R b KQq - 0 11')

    board = chess.Board('r2qk1nr/p2n3p/3p1ppb/2p1p1N1/Q3PP2/2P5/PP4PP/RNB1K2R w KQkq - 0 11')  # !
    # board = chess.Board('7r/p7/2p2R2/P2k4/3PN3/4K2p/1PP3q1/R7 w - - 1 35')

    # board = chess.Board('8/8/5kP1/p2p3P/8/8/2K5/8 w - - 1 2')
    p1 = Player(board=board, color=board.turn, t=500000)

    modBoard = BetterBoard(board, p1.color)
    # print(evaluationFunction(p1, modBoard))
    # print(p1.quiesce(modBoard, p1.color, float('-inf'), float('inf'), 0))
    # print(p1.minimaxQuiesce(modBoard, 0, p1.color, float('-inf'), float('inf')))
    # print(p1.board.phase)
    # print(boardAndPieceEvaluationHelpers.phaseOfGame(board=modBoard))

    board.push(p1.move(board, 1000000))
    # board.push(chess.Move.from_uci('g6g5'))

    # board.push(p1.move(board, 1000000))
