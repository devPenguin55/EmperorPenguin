import random as r
import chess 
import time as t

class Player:
    def __init__(self, board, color, t):
        pass
    
    def move(self, board, t):
        legalMoves = list(board.legal_moves)