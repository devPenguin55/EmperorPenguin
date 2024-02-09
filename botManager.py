import chess.engine
import chess
import chess.pgn
import time
import ultimateMover as player1
import ultimateMover as player2
from stockfish import Stockfish
import os

stockfishPath = 'stockfish-windows-x86-64-avx2.exe'
STOCKFISH = True

stockfish = Stockfish(path=stockfishPath)


def stockfishMove(board, stockfish, timeLimit):
    stockfish.set_fen_position(board.fen())
    moveInfo = stockfish.get_best_move_time(timeLimit)
    bestMove = moveInfo
    return chess.Move.from_uci(bestMove)


games = 50
otherWins = 0
botWins = 0
draws = 0
avgMoves = []
for gameNumber in range(games):
    totalMoves = 0
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

    if not STOCKFISH:
        start = time.time()
        p2 = player2.Player(board2, chess.BLACK, p2_time)
        end = time.time()
        p2_time -= end-start

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

        if move in board.legal_moves:
            board.push(move)
            node = node.add_variation(move)
            movesDone += 1
        else:
            legal_move = False
    if not legal_move:
        if board.turn == chess.WHITE:
            otherWins += 1
            # print("Black wins - illegal move by white")
        else:
            botWins += 1
            # print("White wins - illegal move by black")
    elif p1_time <= 0:
        otherWins += 1
        # print("Black wins on time")
        board.pop()
    elif p2_time <= 0:
        botWins += 1
        # print("White wins on time")
        board.pop()
    elif board.is_checkmate():
        if board.turn == chess.WHITE:
            otherWins += 1
            # print("Black wins - Checkmate!")
        else:
            botWins += 1
            # print("White wins - Checkmate!")
    elif board.is_stalemate():
        draws += 1
        # print("Draw - Stalemate")
    elif board.is_insufficient_material():
        draws += 1
        # print("Draw - Insufficient Material")
    elif board.is_seventyfive_moves():
        draws += 1
        # print("Draw - 75 moves without capture/pawn advancement")
    elif board.is_fivefold_repetition():
        draws += 1
        # print("Draw - position repeated 5 times")
    for move in game.mainline_moves():
        totalMoves += 1
    avgMoves.append(totalMoves)
print(f'{botWins} bot wins, {otherWins} other wins, {draws} draws, {sum(avgMoves)/len(avgMoves)} avg moves')
