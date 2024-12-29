if __name__ == '__main__':
    import chess.engine
    import cProfile
    import chess
    import chess.pgn
    import time
    import ultimateMover as player
    from stockfish import Stockfish
    import random as r
    # do state.pseudo_legal_moves for less time
    # if less time with that then switch else keep as .legal_moves
    DISPLAY = False
    from chessboard import display
    # requires internet?
    # chess.svg.piece(chess.Piece.from_symbol("R"))

    stockfishPath = 'stockfish-windows-x86-64-avx2.exe'
    STOCKFISH = True
    botSide = chess.WHITE

    stockfish = Stockfish(path=stockfishPath)

    def stockfishMove(board, stockfish, timeLimit):
        stockfish.set_fen_position(board.fen())
        # for the best move only
        moveInfo = stockfish.get_best_move_time(10)
        bestMove = moveInfo


        # for the top best moves - variation added
        # moveInfos = stockfish.get_top_moves(5)
        # bestMove = r.choice(moveInfos)['Move']
        return chess.Move.from_uci(bestMove)


    # for benchmarking
    pr = cProfile.Profile()
    pr.enable()


    

    game = chess.pgn.Game()
    node = game
    board = chess.Board()
    board1 = board.copy()
    board2 = board.copy()
    p1_time = 6000
    p2_time = 6000
    start = time.time()
    p1 = player.Player(board1, botSide, p1_time)
    end = time.time()
    p1_time -= end-start

    if not STOCKFISH:
        start = time.time()
        p2 = player.Player(board2, not botSide, p2_time)
        end = time.time()
        p2_time -= end-start


    # starts the game at a random place
    startMoveAmt = 0
    # new = getRandomGameState()
    # for move in new.mainline_moves():
    #     board.push(move)
    #     node = node.add_variation(move)
    #     startMoveAmt += 1


    if DISPLAY:
        displayBoard = display.start()


    legal_move = True
    movesDone = 0
    while p1_time > 0 and p2_time > 0 and not board.is_game_over() and legal_move:
        board_copy = board.copy()
        if board.turn == botSide:
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
            if DISPLAY:
                display.update(board.fen(), displayBoard)
            # time.sleep(1)
        else:
            print('illgal move was', move)
            legal_move = False
        print(f'\n{str(game.mainline_moves())}\n\n')
        


    # pr.print_stats(sort='cumulative')

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

    print()

    print(game)
    print(f'Survived {movesDone-startMoveAmt} moves')
    print(f'Random game moves done at {startMoveAmt//2}')

    # pr.disable()


    if DISPLAY:
        display.terminate()

