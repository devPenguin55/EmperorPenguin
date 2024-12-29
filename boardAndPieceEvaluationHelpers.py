import chess
import betterBoard
import settings

def pawnStructureScore(board:betterBoard.BetterBoard, color):
    score = 0
    pawnSquares = board.moduleBoard.pieces(chess.PAWN, color)
    for square in pawnSquares:
        attackers = board.moduleBoard.attackers(color, square)
        pawnProtection = any(board.moduleBoard.piece_at(attacker).piece_type == chess.PAWN for attacker in attackers)
        if pawnProtection:
            score += 1
        else:
            score -= 2
    return score

def overallPieceProtectionScore(board:betterBoard.BetterBoard, color):
    score = 0
    for pieceType in [chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN, chess.KING]:
        for square in board.moduleBoard.pieces(pieceType, color):
            if board.moduleBoard.attackers(color, square):
                score += 1
            else:
                score -= 2
    return score
    
def passedPawnsScore(board:betterBoard.BetterBoard, color):
    score = 0
    pawnSquares = board.moduleBoard.pieces(chess.PAWN, color)
    for square in pawnSquares:
        if color == chess.WHITE:
            # white pawns will move up
            idx = square
            passed = True
            dist = 0
            while idx+8 <= 63:
                idx += 8
                dist += 1
                if board.moduleBoard.piece_at(idx):
                    passed = False
                    break
        else:
            
            # black pawns will move down
            idx = square
            passed = True
            dist = 0
            while idx-8 >= 0:
                idx -= 8
                dist += 1
                if board.moduleBoard.piece_at(idx):
                    passed = False
                    break
        if passed:
            score += [90, 60, 40, 25, 15, 15, 0][dist]
    return score / board.pieces[chess.PAWN]

def endGameProgression(board):
    maxPieces = 32 # each piece of each color
    minPieces = 2 # 2 kings of each color

    boardPieces = 0
    for color in [chess.WHITE, chess.BLACK]:
        for pieceType in [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
            boardPieces += len(board.moduleBoard.pieces(pieceType, color))

    return (maxPieces - boardPieces) / (maxPieces - minPieces)
        
def phaseOfGame(board:betterBoard.BetterBoard):
    gameProgressionScore = endGameProgression(board)

    if gameProgressionScore < settings.openingThreshold:
        return board.OPENING
    elif gameProgressionScore < settings.middleGameThreshold:
        return board.MIDDLEGAME
    else:
        return board.ENDGAME

# # test cases

# board = chess.Board('8/8/b4B2/P7/5p1P/1kpK4/8/8 w - - 2 49')
# modBoard = betterBoard.BetterBoard(board, chess.WHITE)

# print(pawnStructureScore(modBoard, chess.WHITE))
# print(overallPieceProtectionScore(modBoard, chess.WHITE))
# print(pawnStructureScore(modBoard, chess.BLACK))
# print(overallPieceProtectionScore(modBoard, chess.BLACK))

# print(passedPawnsScore(modBoard, chess.WHITE))

# print()

# print(phaseOfGame(modBoard))
# print(modBoard.phase)
