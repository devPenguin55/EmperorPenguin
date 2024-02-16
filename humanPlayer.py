import io
import chess.engine
import cProfile
import chess
import chess.pgn
import time
import ultimateMover as player1

game = chess.pgn.Game()
node = game
board = chess.Board()
board1 = board.copy()
board2 = board.copy()

p1_time = 1000
p2_time = 1000
start = time.time()
p1 = player1.Player(board1, chess.WHITE, p1_time)
end = time.time()
p1_time -= end-start


legal_move = True
movesDone = 0
while p1_time > 0 and p2_time > 0 and not board.is_game_over() and legal_move:
    board_copy = board.copy()
    if board.turn == chess.WHITE:
        start = time.time()
        move = p1.move(board_copy, p1_time)
        end = time.time()
        p1_time -= end-start

        if move in board.legal_moves:
            board.push(move)
            node = node.add_variation(move)
            movesDone += 1
        else:
            legal_move = False
    else:
        start = time.time()
        move = None
        while True:
            # print(board_copy)
            # print('\na b c d e f g h')
            move = input("User move: ")
            try:
                board_copy.push_san(move)
                break
            except Exception as e:
                print(e)
            print("\n")

        end = time.time()
        p2_time -= end-start
        print(f'\nHuman -> {move}\n')
    
    
    print(f'\n{str(game.mainline_moves())}\n\n')
if not legal_move:
    if board.turn == chess.WHITE:
        print("Black wins - illegal move by white")
    else:
        print("White wins - illegal move by black")
elif p1_time <= 0:
    print("Black wins on time")
    board.pop()
elif p2_time <= 0:
    print("White wins on time")
    board.pop()
elif board.is_checkmate():
    if board.turn == chess.WHITE:
        print("Black wins - Checkmate!")
    else:
        print("White wins - Checkmate!")
elif board.is_stalemate():
    print("Draw - Stalemate")
elif board.is_insufficient_material():
    print("Draw - Insufficient Material")
elif board.is_seventyfive_moves():
    print("Draw - 75 moves without capture/pawn advancement")
elif board.is_fivefold_repetition():
    print("Draw - position repeated 5 times")
print(game)
print(f'Survived {movesDone} moves')
