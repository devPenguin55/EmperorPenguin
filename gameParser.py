import chess.pgn
import chess
import chess.engine
from stockfish import Stockfish

stockfishPath = 'stockfish-windows-x86-64-avx2.exe'

stockfish = Stockfish(path=stockfishPath)

def getStockfishAnalysis(state):
    result = stockfish.get_evaluation()
    if result['type'] == 'cp':
        return abs(result['value']) <= 100
    return False


import random as r
with open('lichess_db_standard_rated_2013-10.pgn') as pgn:
    with open('startingVariations.txt', 'w+') as variationTxt:

        variationTxt.truncate(0)
        variationTxt.seek(0)
        gamesToParse = 50_000
        for gameIndex in range(gamesToParse): # can be whatever, in range of 411,039 though
            game = chess.pgn.read_game(pgn)

            board = game.board()
            i = 0
            cutoff = r.randint(8, 15)
            gameNode = chess.pgn.Game()
            node = gameNode
            for move in game.mainline_moves():
                board.push(move)
                node = node.add_variation(move)
                if i == cutoff*2:
                    break
                i += 1
            if getStockfishAnalysis(board):
                moves = str(gameNode.mainline_moves())

                variationTxt.write(moves)
                variationTxt.write('\n')

            print(f'Parsed game {gameIndex}/{gamesToParse}')
        print(f'Parsed game {gamesToParse}/{gamesToParse}')