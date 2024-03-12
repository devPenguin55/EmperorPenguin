import ultimateMover as player
import chess
import time as t

board = chess.Board(fen='''
                    
8/7k/6pP/6P1/8/p1p5/8/1K6 b - - 0 1

                    ''')
up = chess.WHITE
print(board)

# st  = t.time()
# p2 = player.Player(board, up, 60, experiments=True)
# del p2
# print(t.time()-st)

# quit()

print('Experiments')
st = t.time()
p2 = player.Player(board, up, 60, experiments=True).move(board, 60)
del p2

print('Normal')
st = t.time()
p1 = player.Player(board, up, 60, experiments=False).move(board, 60)
del p1


# LOOK - experimental = True, 56 bot wins, 33 other wins, 11 draws, 112.49 avg moves
# LOOK - experimental = False, 46 bot wins, 31 other wins, 23 draws, 124.71 avg moves