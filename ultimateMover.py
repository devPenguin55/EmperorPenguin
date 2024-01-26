import random as r
import chess 
import time as t


class Player:
    def __init__(self, board, color, t):
        pass
    
    def move(self, board, t):
        def successors(node):
            legalMoves = list(node.legal_moves)
            successorBoards = []
            for move in legalMoves:
                node.push(move)
                successorBoards.append(node)
                node.pop()

            return successorBoards

        for newBoard in successors(board):
            print(newBoard)
            print('---------')

