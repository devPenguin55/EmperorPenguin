import io
import chess.engine
import cProfile
import chess
import chess.pgn
import time
import ultimateMover as player
from stockfish import Stockfish

from chessboard import display
# requires internet?
# chess.svg.piece(chess.Piece.from_symbol("R"))

stockfishPath = 'stockfish-windows-x86-64-avx2.exe'
STOCKFISH = not True

stockfish = Stockfish(path=stockfishPath)


def stockfishMove(board, stockfish, timeLimit):
    stockfish.set_fen_position(board.fen())
    moveInfo = stockfish.get_best_move_time(timeLimit)
    bestMove = moveInfo
    return chess.Move.from_uci(bestMove)


# for benchmarking
pr = cProfile.Profile()
pr.enable()

game = chess.pgn.Game()
node = game
board = chess.Board()
board1 = board.copy()
board2 = board.copy()
p1_time = 1000
p2_time = 1000
start = time.time()
p1 = player.Player(board1, chess.WHITE, p1_time)
end = time.time()
p1_time -= end-start

if not STOCKFISH:
    start = time.time()
    p2 = player.Player(board2, chess.BLACK, p2_time)
    end = time.time()
    p2_time -= end-start


displayBoard = display.start()


legal_move = True
movesDone = 0
while p1_time > 0 and p2_time > 0 and not board.is_game_over() and legal_move:
    board_copy = board.copy()
    if board.turn == chess.WHITE:
        start = time.time()
        move = p1.move(board_copy, p1_time)
        end = time.time()
        p1_time -= end-start
    else:
        if not STOCKFISH:
            start = time.time()
            move = p2.move(board_copy, p2_time)
            end = time.time()
            p2_time -= end-start
        else:
            start = time.time()
            move = stockfishMove(board_copy, stockfish, p2_time)
            end = time.time()
            p2_time -= end-start
            print(f'\nStockfish -> {move}\n')

    if move in board.legal_moves:
        board.push(move)
        node = node.add_variation(move)
        movesDone += 1
        display.update(board.fen(), displayBoard)
        time.sleep(1)
    else:
        legal_move = False
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


pr.disable()

time.sleep(30)
display.terminate()

# import time as t
# print('Stats coming in 10 seconds')
# t.sleep(10)
# pr.print_stats(sort='cumulative')


def whiteAccuracyFromPgn(game):
    board = chess.Board()

    enginePath = stockfishPath
    engine = chess.engine.SimpleEngine.popen_uci(enginePath)

    totalMoves = 0
    accurateMoves = 0

    for move in game.mainline_moves():
        totalMoves += 1
        evaluation = engine.analyse(board, chess.engine.Limit(time=0.1))
        actualResult = game.headers["Result"]

        # see if white's move was accurate
        try:
            if (evaluation["score"].relative.score() > 0) == ("1-0" in actualResult):
                accurateMoves += 1
        except:
            pass

        board.push(move)

    # accuracy
    whiteAccuracy = 100 - (accurateMoves / totalMoves) * 100
    return whiteAccuracy


print('Assembling accuracy...')
whiteAccuracy = whiteAccuracyFromPgn(game)
print(f"White player (Bot) weird accuracy (dont trust): {whiteAccuracy:.2f}%")
