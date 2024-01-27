import random as r
import chess 
import time as t


class Player:
    def __init__(self, board, color, t):
        self.color = color
    
    def evaluationFunction(self, board):
        # fill this part out
        return 5

    def move(self, board, t):
        AGENTS = 2

    
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
        def evaluate(state, depth, agent):
            if depth/AGENTS == wantedDepth:
                return self.evaluationFunction(state)
            else:
                if agent == 0:
                    return maxVal(state, depth+1, agent)
                else:
                    return minVal(state, depth+1, agent)

        def maxVal(state, depth, agent):
            s = getSuccessors(state, agent)
            if not s:
                return self.evaluationFunction(state)
            val = float("-inf")
            for successor in s:
                val = max(val, evaluate(successor, depth, getNextAgent(agent)))
            return val
        
        def minVal(state, depth, agent):
            s = getSuccessors(state, agent)
            if not s:
                return self.evaluationFunction(state)
            val = float("inf")
            for successor in s:
                val = min(val, evaluate(successor, depth, getNextAgent(agent)))
            return val
        
        wantedDepth = 2

        vals = []
        for successor in getSuccessors(board, self.color):
            # get the minimax of the layer after you to get correct depth
            # start with the next agent, as you are starting 1 depth lower in the tree
            vals.append(evaluate(successor, 1, getNextAgent(self.color)))
        print(vals)
        actions = list(board.legal_moves)
        return actions[vals.index(max(vals))]
