import chess
import chess.pgn
import time
import ultimateMover as player1
# import randomMover as player2
import ultimateMover as player2

# for benchmarking
import cProfile
pr = cProfile.Profile()
pr.enable()
# def getSuccessors(curBoard, turn):
#     # set the node to the current board we are on
#     node = curBoard

#     # have the node's turn be whatever turn we want
#     node.turn = turn

#     # get the legal moves and generate a list of boards with these moves
#     legalMoves = list(node.legal_moves)
#     successorBoards = []
#     for move in legalMoves:
#         node.push(move)
#         successorBoards.append(node)
#         node.pop()
#     # print(successorBoards)
#     return successorBoards
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

start = time.time()
p2 = player2.Player(board2, chess.BLACK, p2_time)
end = time.time()
p2_time -= end-start

legal_move = True

while p1_time > 0 and p2_time > 0 and not board.is_game_over() and legal_move:
    board_copy = board.copy()
    if board.turn == chess.WHITE:
        start = time.time()
        move = p1.move(board_copy, p1_time)
        end = time.time()
        p1_time -= end-start
    else:
        start = time.time()
        move = p2.move(board_copy, p2_time)
        end = time.time()
        p2_time -= end-start

    if move in board.legal_moves:
        board.push(move)
        node = node.add_variation(move)
    else:
        legal_move = False

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

pr.disable()
# import time as t
# print('Stats coming in 10 seconds')
# t.sleep(10)
# pr.print_stats(sort='cumulative')
