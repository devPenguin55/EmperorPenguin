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

    value, pv = self.minimax(boardCopy, wantedDepth, color, a, b, st,
                             endTime, tt, killerMoves, iterativeDeepeningDepth, self.PVN)
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
        self.timeToThink = t/40
        self.timeToThink = 2  # 5 IS ONLY FOR HUMAN GAME - REMOVE IF NOT DOING A HUMAN GAME

        self.nodesVisited = 0
        self.prunes = 0
        self.transpositionMatches = 0

        self.HASH_EXACT = 1
        self.HASH_ALPHA = 2
        self.HASH_BETA = 3
        self.CHECKMATE = 9999999

        self.PVN = []
        self.CN = []
        self.AN = []

        self.killerMoves = []

        self.minDepth = settings.minDepth

        self.extendNextMoveDepthFromGameOverNodeSeen = False

        self.currentTopDepth = 0

    def bookMove(self, state: chess.Board):
        with chess.polyglot.open_reader("C:\\ChessAi\\UltimateChessAI\\bookMoves.bin") as reader:
            entries = list(reader.find_all(state))
            if entries:
                results = sorted([(i.move, i.weight) for i in entries], key=lambda x: x[-1], reverse=True)
                results = results[0:min(len(results), 2)]
                return r.choice(results)[0]
            else:
                return False

    def quiesce(self, state: BetterBoard, agent, a, b, depth):
        self.nodesVisited += 1
        evaluation = evaluationFunction(self, state, forceAgent=agent)
        if evaluation >= b:
            return b

        # if depth == 4:
        #     return evaluation

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
        best = float('-inf') if agent == self.color else float('inf')

        moves = [
            move for move in state.moduleBoard.legal_moves if state.moduleBoard.is_capture(move)]

        if not moves or depth >= 2:
            # print(state.moduleBoard.fen())
            ttEntry = self.transpositionTable.lookup(state.moduleBoard)
            # true depth -> depth - self.currentTopDepth
            if ttEntry is not None and ttEntry.depth >= depth:
                # print(depth, ttEntry.depth)
                # ttEntry.depth >= depth because a depth further from is a far deeper depth than one lower
                # so a lower depth means that it has been searched more deeply
                self.transpositionMatches += 1
                return ttEntry.value
            else:
                result = evaluationFunction(self, state)
                self.transpositionTable.store(
                    state.moduleBoard, self.HASH_EXACT, depth, result)

                return result

        for move in moves:
            state.push(move)
            val = self.minimaxQuiesce(state, depth+1, not agent, a, b)
            state.pop()

            if agent == self.color:
                best = max(best, val)
            else:
                best = min(best, val)

            if agent == self.color:
                a = max(a, val)
            else:
                b = min(b, val)

            if a >= b:
                break

        return best

    def minimax(self, state: BetterBoard, depth, agent, a, b, startTime, maxTime, iterativeDeepeningDepth, pv):

        # iterativeDeepeningDepth 0, 1, 2, 3 means depth 1, 2, 3, 4
        if t.time()-startTime > maxTime and iterativeDeepeningDepth > self.minDepth:
            # if we have exceeded the time given, raise an error to end all minimax processes
            # only may happen if at least 1 depth has been searched
            1/0

        # do not return pv at terminal / leaf nodes

        ttEntry = self.transpositionTable.lookup(state.moduleBoard)
        depthFromRoot = depth
        
        # print(f'{depth} ply left, {self.currentTopDepth} ply to search to, {depthFromRoot} ply from the root')
        if ttEntry is not None and ttEntry.depth >= depthFromRoot:
            # print(f'     -> TT match at {ttEntry.depth} ply from the root')
            # print(depth, ttEntry.depth)
            # ttEntry.depth <= depth because a depth closer to 0 is a far deeper depth than one higher
            # so a lower depth means that it has been searched more deeply
            self.transpositionMatches += 1
            if ttEntry.flag == self.HASH_EXACT:
                # exact value of the state
                return ttEntry.value, []
            elif ttEntry.flag == self.HASH_ALPHA:
                if ttEntry.value <= a:
                    return a, []
            elif ttEntry.flag == self.HASH_BETA:
                if ttEntry.value >= b:
                    return b, []

            # our best move is so good that the opponent will never take it, so prune it!
            if a >= b:
                self.prunes += 1
                return ttEntry.value

        self.nodesVisited += 1
        hasReachedGameOver = state.moduleBoard.is_game_over(claim_draw=True)
        if depth == 0 or hasReachedGameOver:
            if hasReachedGameOver:
                self.gameOverStatesFound += 1

            if settings.quiesce and [move for move in state.moduleBoard.legal_moves if state.moduleBoard.is_capture(move)]:
                # result = self.quiesce(state, agent, a, b, 0)
                result = self.minimaxQuiesce(state, self.currentTopDepth, agent, a, b)
                return result, []
            else:
                result = evaluationFunction(self, state)
                # tt.store(state.moduleBoard, self.HASH_EXACT, depth, result)
                self.transpositionTable.store(state.moduleBoard, self.HASH_EXACT, depthFromRoot, result)

                return result, []

            result = evaluationFunction(self, state)
            self.transpositionTable.store(state.moduleBoard, self.HASH_EXACT, depthFromRoot, result)

            return result, []

        flag = self.HASH_ALPHA
        if agent == self.color:
            best = float('-inf')

            legalMoves = orderMoves(self, state, state.moduleBoard.legal_moves,
                                    agent, depth, pv, self.transpositionTable, self.killerMoves)

            for move in legalMoves:
                state.push(move)
                val, childPv = self.minimax(
                    state, depth-1, not agent, a, b, startTime, maxTime, iterativeDeepeningDepth, pv)
                state.pop()



                if val > best:
                    best = val
                    pv = [(move, depth)] + childPv
                    flag = self.HASH_EXACT
                    # print(f'Depth {depth} pv {pv}')
                a = max(a, val)

                if a >= b:
                    self.prunes += 1
                    self.killerMoves.append(move)
                    self.transpositionTable.store(
                        state.moduleBoard, self.HASH_BETA, depthFromRoot, best)
                    return best, []
        else:
            best = float('inf')
            legalMoves = orderMoves(self, state, state.moduleBoard.legal_moves,
                                    agent, depth, pv, self.transpositionTable, self.killerMoves)


            for move in legalMoves:
                state.push(move)
                val, childPv = self.minimax(
                    state, depth-1, not agent, a, b, startTime, maxTime, iterativeDeepeningDepth, pv)
                state.pop()


                if val < best:
                    best = val
                    pv = [(move, depth)] + childPv
                    flag = self.HASH_EXACT
                    # print(f'Depth {depth} pv {pv}')

                b = min(b, val)

                if a >= b:
                    self.prunes += 1
                    self.killerMoves.append(move)
                    self.transpositionTable.store(
                        state.moduleBoard, self.HASH_BETA, depthFromRoot, best)
                    return best, []
            

        self.transpositionTable.store(state.moduleBoard, flag, depthFromRoot, a)

        return best, pv

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

        def searchFromRootMinimax(wantedDepth, st, endTime, boardCopy: BetterBoard, iterativeDeepeningDepth):
            global nodesVisited
            bestVal = float('-inf')
            bestMove = None
            a, b = float('-inf'), float('inf')
            orderedMoves = orderMoves(self, boardCopy, boardCopy.moduleBoard.legal_moves,
                                      self.color, wantedDepth, self.PVN, self.transpositionTable, self.killerMoves)
            self.nodesVisited += 1
            for move in orderedMoves:
                boardCopy.push(move)
                val, pv = self.minimax(boardCopy, wantedDepth-1, not self.color,
                                       a, b, st, endTime, iterativeDeepeningDepth, [])  # get values
                boardCopy.pop()
                if val > bestVal:
                    bestVal = val
                    bestMove = move
                    self.PVN = [(move, wantedDepth)] + pv

                a = max(a, val)

                if a >= b:
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

            # self.nodesVisited   = sum([i for _, _, i, _, _, _, _ in results])
            # self.transpositionMatches = sum([i for _, _, _, i, _, _, _ in results])
            # self.gameOverStatesFound  = sum([i for _, _, _, _, i, _, _ in results])
            # self.prunes  = sum([i for _, _, _, _, _, i, _ in results])

            if bestMove is None:
                bestVal, pv = self.minimax(boardCopy, wantedDepth, self.color, float(
                    '-inf'), float('inf'), st, endTime, iterativeDeepeningDepth, self.PVN)
                self.PVN = pv
                try:
                    bestMove = pv[0][0]
                except Exception:
                    return bestMove, bestVal

            if (len(self.PVN) != wantedDepth and wantedDepth != 1) or bestVal == float('inf') or bestVal == float('-inf'):
                print(f'           |__ emperorPenguin pv incorrect for depth {wantedDepth} -> bad search result, cancelling search from here')
                raise ZeroDivisionError

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
            # use 'or' between
            totalNodesVisited = 0
            while (t.time()-startedTime < timeAllocation and curDepth <= depthLimit) or (iterativeDeepeningDepth <= self.minDepth):
                try:
                    self.transpositionTable.clear()
                    self.transpositionMatches = 0
                    self.gameOverStatesFound = 0
                    self.prunes = 0
                    self.nodesVisited = 0

                    self.currentTopDepth = curDepth

                    bestMoveFound, curVal = searchFromRootMinimax(
                        curDepth, startedTime, timeAllocation, boardCopy, iterativeDeepeningDepth)
                    totalNodesVisited += self.nodesVisited
                    if self.gameOverStatesFound != 0:
                        self.extendNextMoveDepthFromGameOverNodeSeen = True

                    if curVal == -self.CHECKMATE:
                        curVal = f'losing mate seen at depth {curDepth}'
                    elif curVal == self.CHECKMATE:
                        curVal = f'winning mate seen at depth {curDepth}'
                    print(f'       |___ Iterative Deepening - depth {curDepth}, PV -> {[(i[0].uci(), i[1]) for i in self.PVN]}, move {bestMoveFound}, eval {curVal}, gameOverNodes {self.gameOverStatesFound}, prunes {self.prunes}, pos {self.nodesVisited}, tt size {len(self.transpositionTable)}, tt matches {self.transpositionMatches}, took {round(t.time()-lastTime, 2)}s, cum {round(t.time()-startedTime, 2)}s')

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
            self.nodesVisited = totalNodesVisited
            return bestMoveFound

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
        print('Old Version')

        timeToUse, stableness = timeFromState(self.board)

        triggerNextMoveDepthBack = False
        self.extendNextMoveDepthFromGameOverNodeSeen = False # ! DO NOT USE
        if self.extendNextMoveDepthFromGameOverNodeSeen:
            self.extendNextMoveDepthFromGameOverNodeSeen = False
            self.minDepth += 1
            settings.minDepth += 1
            triggerNextMoveDepthBack = True

        timeToUse = 100
        # self.transpositionTable.clear()
        # if False:

        bestMove = iterativeDeepening(timeAllocation=timeToUse, depthLimit=55)
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

        return bestMove


if __name__ == '__main__':
    # board = chess.Board('r1bqkbr1/p3pppp/1p3n2/6B1/3N4/2P2P2/PP4PP/R2QKB1R b KQq - 0 11')
    # board = chess.Board('8/8/6n1/4b3/k2P4/4P3/8/4K3 w - - 0 1')
    # board = chess.Board('r1bqk2r/pppp1p1p/5np1/3Pp3/1b2P3/8/1PPN1PPP/R1BQKBNR w KQkq - 0 7')

    board = chess.Board('r3kb1r/p1pb1ppp/2p2n2/3Pp2q/P5P1/2N1BP2/1PP1N2P/R2Q1RK1 b kq - 0 13') # !

    # board = chess.Board('2r3k1/pp3ppp/1bp5/5N2/8/P3P3/1P3P2/2R1KB2 w - - 0 28')

    p1 = Player(board=board, color=board.turn, t=500000)

    modBoard = BetterBoard(board, p1.color)
    # print(evaluationFunction(p1, modBoard))
    # print(p1.quiesce(modBoard, p1.color, float('-inf'), float('inf'), 0))
    # print(p1.minimaxQuiesce(modBoard, 0, p1.color, float('-inf'), float('inf')))
    # print(p1.board.phase)
    # print(boardAndPieceEvaluationHelpers.phaseOfGame(board=modBoard))
    
    print(p1.move(board, 1000000))