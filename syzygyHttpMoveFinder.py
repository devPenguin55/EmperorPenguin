import requests
import json
import chess

def findBestMoveForEndgame(board:chess.Board):
    result = requests.get(f'http://tablebase.lichess.ovh/standard?fen={board.fen().replace(' ', '_')}').content

    moveResult = json.loads(result)['moves'][0]

    if not moveResult['dtz'] and not moveResult['dtm'] and not moveResult['dtw']:
        return None
    else:
        print(moveResult)
        return moveResult['uci']
    
# board = chess.Board('4k3/6KP/8/8/8/8/7p/8 w - - 0 1')
# # board = chess.Board('rnbqkbnr/pppppppp/8/8/8/2P5/PP1PPPPP/RNBQKBNR b KQkq - 0 1')

# print(findBestMoveForEndgame(board))