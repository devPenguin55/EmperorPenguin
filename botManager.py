import chess.engine
import chess
import chess.pgn
import time
import ultimateMover as player
from stockfish import Stockfish
from gameReader import getRandomGameState
import os

# is move ordering doing any good?

stockfishPath = 'stockfish-windows-x86-64-avx2.exe'
STOCKFISH = not True

stockfish = Stockfish(path=stockfishPath)

def stockfishMove(board, stockfish, timeLimit):
    stockfish.set_fen_position(board.fen())
    moveInfo = stockfish.get_best_move_time(1)
    bestMove = moveInfo
    return chess.Move.from_uci(bestMove)

playerTypes = [True, False]
if not STOCKFISH:
    # true false   is the experiments
    # white black
    playerTypes = [True]
for playerType in playerTypes:
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

        new = getRandomGameState()
        for move in new.mainline_moves():
            board.push(move)
            node = node.add_variation(move)


        board1 = board.copy()
        board2 = board.copy()
        p1_time = 60
        p2_time = 60
        start = time.time()
        p1 = player.Player(board1, chess.WHITE, p1_time, experiments=playerType)
        end = time.time()
        p1_time -= end-start

        if not STOCKFISH:
            start = time.time()
            p2 = player.Player(board2, chess.BLACK, p2_time, experiments=not playerType)
            end = time.time()
            p2_time -= end-start

        legal_move = True
        movesDone = 0
        while p1_time > 0 and p2_time > 0 and not board.is_game_over() and legal_move:
            board_copy = board.copy()
            if board.turn == True:
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
                # time.sleep(1)
            else:
                legal_move = False
            print(f'\n{str(game.mainline_moves())}\n\n')
        
        if not legal_move:
            if board.turn == chess.WHITE:
                otherWins += 1
                print("Black wins - illegal move by white")
            else:
                botWins += 1
                print("White wins - illegal move by black")
        elif p1_time <= 0:
            otherWins += 1
            print("Black wins on time")
            board.pop()
        elif p2_time <= 0:
            botWins += 1
            print("White wins on time")
            board.pop()
        elif board.is_checkmate():
            if board.turn == chess.WHITE:
                otherWins += 1
                print("Black wins - Checkmate!")
            else:
                botWins += 1
                print("White wins - Checkmate!")
        elif board.is_stalemate():
            draws += 1
            print("Draw - Stalemate")
        elif board.is_insufficient_material():
            draws += 1
            print("Draw - Insufficient Material")
        elif board.is_seventyfive_moves():
            draws += 1
            print("Draw - 75 moves without capture/pawn advancement")
        elif board.is_fivefold_repetition():
            draws += 1
            print("Draw - position repeated 5 times")
        print(game)
        for move in game.mainline_moves():
            totalMoves += 1
        avgMoves.append(totalMoves)
    print(f'LOOK - experimental = {playerType}, {botWins} bot wins, {otherWins} other wins, {draws} draws, {sum(avgMoves)/len(avgMoves)} avg moves')
