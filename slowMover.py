import random
import chess
import time

class Player:
    def __init__(self, board, color, t):
        pass
    
    def move(self, board, t):
        time.sleep(random.random())
        return random.choice(list(board.legal_moves))