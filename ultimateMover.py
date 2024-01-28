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
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        self.knights = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50,
        ]
        self.bishops = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20,
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
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
             -5,  0,  5,  5,  5,  5,  0, -5,
              0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]
        self.kingMiddleGame = [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
             20, 20,  0,  0,  0,  0, 20, 20,
             20, 30, 10,  0,  0, 10, 30, 20
        ]
        self.kingEndGame = [
            -50,-40,-30,-20,-20,-30,-40,-50,
            -30,-20,-10,  0,  0,-10,-20,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-30,  0,  0,  0,  0,-30,-30,
            -50,-30,-30,-30,-30,-30,-30,-50
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

    def evaluationFunction(self, board, color):
        pieces = [
            (chess.KING, 20_000), 
            (chess.QUEEN, 900), 
            (chess.ROOK, 500),
            (chess.BISHOP, 330),
            (chess.KNIGHT, 320),
            (chess.PAWN, 100), 
        ]

        def pieceCount(piece, color):
            # get amt of pieces on the board that are a certain color and type
            return len(board.pieces(piece, color))

        material = 0
        for piece, value in pieces:
            # in chess module, white is True, black is False
            # therefore, to get the next agent, just do not agent
            # True -> False, False -> True
            material += value * (pieceCount(piece, color)-pieceCount(piece, not color))


        return material
    
    

    def move(self, board, t):
        AGENTS = 2
        testBoard = chess.Board()
        m = testBoard.piece_map()
        pieces = [c for c in m]
        print(pieces)
        print(testBoard.piece_at(pieces[0]))
        quit()
        def getSuccessors(curBoard, turn):
            # set the node to the current board we are on
            node = curBoard

            # have the node's turn be whatever turn we want
            node.turn = turn

            # get the legal moves and generate a list of boards with these moves
            legalMoves = list(node.legal_moves)
            successorBoards = []
            for move in legalMoves:
                node.push(move)
                successorBoards.append(node.copy())
                node.pop()
            return successorBoards
        
        def getNextAgent(agent):
            # in chess module, white is True, black is False
            # therefore, to get the next agent, just do not agent
            # True -> False, False -> True
            return not agent 

        # standard minimax code
        def evaluate(state, depth, agent, a, b):
            if depth/AGENTS == wantedDepth:
                return self.evaluationFunction(state, agent)
            else:
                if agent == self.color:
                    return maxVal(state, depth+1, agent, a, b)  
                else:
                    return minVal(state, depth+1, agent, a, b)

        def maxVal(state, depth, agent, a, b):
            s = getSuccessors(state, agent)
            if not s:
                return self.evaluationFunction(state, agent)
            
            val = float('-inf')
            for successor in s:
                val = max(val, evaluate(successor, depth, getNextAgent(agent), a, b))
                if val > b:
                    return val
                a = max(a, val)
            return val
        
        def minVal(state, depth, agent, a, b):
            s = getSuccessors(state, agent)
            if not s:
                return self.evaluationFunction(state, agent)
            
            val = float('inf')
            for successor in s:
                val = min(val, evaluate(successor, depth, getNextAgent(agent), a, b))
                if val < a:
                    return val
                b = min(b, val)
            return val
        
        
        wantedDepth = 1.5
    
        vals = []
        a = float('-inf')
        b = float('inf')
        v = float('-inf')
        actions = list(board.legal_moves)

        children = getSuccessors(board, self.color)
        for i in range(len(actions)):
            successor = children[i]
            # get the minimax of the layer after you to get correct depth
            # start with the next agent, as you are starting 1 depth lower in the tree

            # with self.color it works?
            v = max(v, evaluate(successor, 1, getNextAgent(self.color), a, b))
            vals.append(v)
            a = max(a, v)
        
        print(vals)
        print(board)
        print(self.color)
        return actions[vals.index(v)]
