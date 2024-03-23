import ultimateMover as player
import chess
import time as t
import random as r
from betterBoard import BetterBoard 

board = chess.Board(fen='''
                    
r1b1kb1r/pp2pppp/2n2n2/q1pp2N1/P7/N1P4P/1P1PPPP1/R1BQKB1R b KQkq - 1 6
                    ''')
up = chess.BLACK
print(board)


boardn = BetterBoard(board.copy(), up)


pawns = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5, -10,  0,  0, -10, -5,  5,
    5, 10, 10, -20, -20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]
knights = [
    -50, -40, -30, -30, -30, -30, -40, -50,
    -40, -20,  0,  0,  0,  0, -20, -40,
    -30,  0, 10, 15, 15, 10,  0, -30,
    -30,  5, 15, 20, 20, 15,  5, -30,
    -30,  0, 15, 20, 20, 15,  0, -30,
    -30,  5, 10, 15, 15, 10,  5, -30,
    -40, -20,  0,  5,  5,  0, -20, -40,
    -50, -40, -30, -30, -30, -30, -40, -50,
]
bishops = [
    -20, -10, -10, -10, -10, -10, -10, -20,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  5, 10, 10,  5,  0, -10,
    -10,  5,  5, 10, 10,  5,  5, -10,
    -10,  0, 10, 10, 10, 10,  0, -10,
    -10, 10, 10, 10, 10, 10, 10, -10,
    -10,  5,  0,  0,  0,  0,  5, -10,
    -20, -10, -10, -10, -10, -10, -10, -20,
]
rooks = [
    0,  0,  0,  0,  0,  0,  0,  0,
    5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    0,  0,  0,  5,  5,  0,  0,  0
]
queen = [
    -20, -10, -10, -5, -5, -10, -10, -20,
    -10,  0,  0,  0,  0,  0,  0, -10,
    -10,  0,  5,  5,  5,  5,  0, -10,
    -5,  0,  5,  5,  5,  5,  0, -5,
    0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0, -10,
    -10,  0,  5,  0,  0,  0,  0, -10,
    -20, -10, -10, -5, -5, -10, -10, -20
]
kingMiddleGame = [
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -30, -40, -40, -50, -50, -40, -40, -30,
    -20, -30, -30, -40, -40, -30, -30, -20,
    -10, -20, -20, -20, -20, -20, -20, -10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]
kingEndGame = [
    -50, -40, -30, -20, -20, -30, -40, -50,
    -30, -20, -10,  0,  0, -10, -20, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 30, 40, 40, 30, -10, -30,
    -30, -10, 20, 30, 30, 20, -10, -30,
    -30, -30,  0,  0,  0,  0, -30, -30,
    -50, -30, -30, -30, -30, -30, -30, -50
]

if up == chess.BLACK:
            
    # black will invert the tables
    pawns.reverse()
    bishops.reverse()
    knights.reverse()
    queen.reverse()
    rooks.reverse()
    kingMiddleGame.reverse()
    kingEndGame.reverse()

def evaluationFunction(state:chess.Board):
        print(state)
        pieces = {
            chess.KING: 200,
            chess.QUEEN: 90,
            chess.ROOK: 50,
            chess.BISHOP: 30,
            chess.KNIGHT: 30,
            chess.PAWN: 10,
        }
        stringToPiece = {
            'p': chess.PAWN,
            'r': chess.ROOK,
            'n': chess.KNIGHT,
            'b': chess.BISHOP,
            'q': chess.QUEEN,
            'k': chess.KING
        }
        agent = up
        if state.is_checkmate():
            if state.turn == agent:
                return -9999999
            else:
                return 9999999
    
        inEndgame = state.pieces(chess.QUEEN, agent) == 0 and state.pieces(chess.QUEEN, not agent) == 0

        if not inEndgame:
            kingDist = 0
        else:
            # move king close to other king to get checkmate in endgame
            try:
                kingDist = 20 * (1/(chess.square_distance(state.king(agent), state.king(not agent))))
            except:
                kingDist = 0

        
        pieceMap = state.piece_map()

        def transformIndex(index):
            # get row and column
            row = index // 8
            col = index % 8

            # get the new row
            newRow = 7 - row

            # find new index
            newIndex = newRow * 8 + col

            return newIndex
        mappedPieces = {
            'p': pawns,
            'n': knights,
            'b': bishops,
            'r': rooks,
            'q': queen,
            'k': kingMiddleGame
        }
        locationScore = 0
        material = 0
        for index in pieceMap:
            piece, index = str(pieceMap[index]), index
            
            if agent == True and piece == piece.lower():
                side = -1
            elif agent == False and piece == piece.upper():
                side = -1
            else:
                side = 1
            
            pieceChessType = stringToPiece[piece.lower()]
            table = mappedPieces[piece.lower()]
            locationScore += table[transformIndex(index)] * side
            if piece == 'P':              
                print(piece, side, table[transformIndex(index)], transformIndex(index))
            material += pieces[pieceChessType] * side

        return locationScore, material


print(evaluationFunction(board))
print(boardn.locationScore)
print()


moves = list(boardn.moduleBoard.legal_moves)
passed = 0
for move in moves:
    print('passed', passed, '/', len(moves), 'case')
    board.push(move)
    boardn.push(move)
    correctlocation, correctmaterial = evaluationFunction(board)
    if correctlocation != boardn.locationScore:
        print('\nfailed on')
        print(move, correctlocation, boardn.locationScore)
        quit()
    print(correctlocation)
    print(boardn.locationScore)
    print()
    board.pop()
    boardn.pop()
    passed += 1

print('passed all of the location test cases')
# t.sleep(2)
passed = 0
for move in moves:
    print('passed', passed, '/', len(moves), 'case')
    board.push(move)
    boardn.push(move)
    correctlocation, correctmaterial = evaluationFunction(board)
    if correctmaterial != boardn.material:
        print('\nfailed on')
        print(move, correctmaterial, boardn.material)
        quit()
    print(move)
    print(correctmaterial)
    print(boardn.material)
    print()
    board.pop()
    boardn.pop()
    passed += 1
print('passed all of the material test cases ')

print(evaluationFunction(board))
print(boardn.locationScore)
print()

randomMove = moves[0]
board.push(randomMove)
boardn.push(randomMove)


moves = list(board.legal_moves)[::-1]
passed = 0
for move in moves:
    print('passed', passed, '/', len(moves), 'case')
    board.push(move)
    boardn.push(move)
    correctlocation, correctmaterial = evaluationFunction(board)
    if correctlocation != boardn.locationScore:
        print('\nfailed on')
        print(move, correctlocation, boardn.locationScore)
        quit()
    print(correctlocation)
    print(boardn.locationScore)
    print()
    board.pop()
    boardn.pop()
    passed += 1

print('passed all of the location test cases 2')
# t.sleep(2)
passed = 0
for move in moves:
    print('\npassed', passed, '/', len(moves), 'case\n')
    board.push(move)
    boardn.push(move)
    correctlocation, correctmaterial = evaluationFunction(board)
    if correctmaterial != boardn.material:
        print('\nfailed on')
        print(move, correctmaterial, boardn.material)
        quit()
    print(move)
    print(correctmaterial)
    print(boardn.material)
    print()
    board.pop()
    boardn.pop()
    passed += 1
print('passed all of the material test cases 2')






# st  = t.time()
# p2 = player.Player(board, up, 60, experiments=True)
# del p2
# print(t.time()-st)

# quit()

# print('Experiments')
# st = t.time()
# p2 = player.Player(board, up, 60).move(board, 60)
# del p2  

# print('Normal')
# st = t.time()
# p1 = player.Player(board, up, 60).move(board, 60)
# del p1


