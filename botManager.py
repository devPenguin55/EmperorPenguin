import chess.engine
import chess
import chess.pgn
import time
import emperorPenguin as player
import emperorPenguinOLD as oldVersion
from stockfish import Stockfish
from gameReader import getRandomGameState
import multiprocessing as mp
import time as t

matchTime = 6000 # 50 minute game

def simulateGame(identifier):
    stockfishPath = 'stockfish-windows-x86-64-avx2.exe'
    STOCKFISH = False

    stockfish = Stockfish(path=stockfishPath)

    def stockfishMove(board, stockfish, timeLimit):
        stockfish.set_fen_position(board.fen())
        moveInfo = stockfish.get_best_move_time(10)
        bestMove = moveInfo
        return chess.Move.from_uci(bestMove)

    def getEvaluation(board):
        stockfish.set_fen_position(board.fen())
        return stockfish.get_evaluation()
    
    print('PID', identifier)
    totalMoves = 0
    game = chess.pgn.Game()
    node = game
    board = chess.Board()


    otherWins = 0
    botWins = 0
    draws = 0
    botWinOnTime = 0
    otherWinOnTime = 0

    # gets random board states that are still somewhat equal
    evaluation = float('inf')
    while evaluation > 30 or evaluation < -30:
        del board
        del game 
        del node

        board = chess.Board()
        game = chess.pgn.Game()
        node = game

        new = getRandomGameState()
        amtMoves = 0
        for move in new.mainline_moves():
            amtMoves += 1
            board.push(move)
            node = node.add_variation(move)
        evaluation = getEvaluation(board)
        if evaluation.get('type', '') == 'cp':
            evaluation = evaluation.get('value', float('inf'))
        else:
            evaluation = float('inf')
        if amtMoves < 16:
            evaluation = float('inf')
        print(getEvaluation(board))
    print(getEvaluation(board))
    print(game)

    board1 = board.copy()
    board2 = board.copy()
    p1_time = matchTime
    p2_time = matchTime
    start = time.time()
    p1 = player.Player(board1, chess.WHITE, p1_time)
    # p1 = oldVersion.Player(board2, chess.BLACK, p2_time)
    end = time.time()
    p1_time -= end-start

    if not STOCKFISH:
        start = time.time()
        p2 = oldVersion.Player(board2, chess.BLACK, p2_time)
        # p2 = player.Player(board1, chess.WHITE, p1_time)
        end = time.time()
        p2_time -= end-start
    else:
        p2 = None

    legal_move = True
    movesDone = 0

    while p1_time > 0 and p2_time > 0 and not board.is_game_over(claim_draw=True) and legal_move:
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
        print(f'\n{identifier}            {str(game.mainline_moves())}\n\n')
        
    if not legal_move:
        if board.turn == p1.color:
            otherWins += 1
            print("Other wins - illegal move by bot")
        else:
            botWins += 1
            print("Bot wins - illegal move by other")
    elif p1_time <= 0:
        otherWinOnTime += 1
        print("Other wins on time")
        board.pop()
    elif p2_time <= 0:
        botWinOnTime += 1
        print("Bot wins on time")
        board.pop()
    elif board.is_checkmate():
        if board.turn == p1.color:
            otherWins += 1
            print("Other wins - Checkmate!")
        else:
            botWins += 1
            print("Bot wins - Checkmate!")
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
    del p1
    del p2
    del game
    del node
    del board

    print(f'LOOK - {botWins} bot wins, {otherWins} other wins, {draws} draws')
    return (botWins, otherWins, botWinOnTime, otherWinOnTime, draws, totalMoves)

if __name__ == '__main__':
    games = 1

    with mp.Pool(min(games, 20)) as pool:
        results = pool.map(simulateGame, range(games))
    print(results)
    processedResults = []
    processedResults.append(sum([i for i, _, _, _, _, _ in results]))
    processedResults.append(sum([i for _, i, _, _, _, _ in results]))
    processedResults.append(sum([i for _, _, i, _, _, _ in results]))
    processedResults.append(sum([i for _, _, _, i, _, _ in results]))
    processedResults.append(sum([i for _, _, _, _, i, _ in results]))
    processedResults.append(sum([i for _, _, _, _, _, i in results]) / len(results))
    print(f'results -> {processedResults[0]} bot wins, {processedResults[1]} opponent wins, {processedResults[2]} bot wins on time, {processedResults[3]} opponent wins on time, {processedResults[4]} draws, {processedResults[5]} avg total moves, match time -> {matchTime/60} minutes')
    # print(f'LOOK - {botWins} bot wins, {otherWins} other wins, {draws} draws, {sum(avgMoves)/len(avgMoves)} avg moves')   