import chess
import betterBoard
import settings
from collections import Counter
import pprint

def pawnStructureScore(board:betterBoard.BetterBoard, color):
    '''
    take all pawns we have, go through each and see if it has attackers of 
    the same color. if it does, add 1, else subtract 2
    '''
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
            attackersOnSquare = board.moduleBoard.attackers(color, square)
            if attackersOnSquare:
                # score += len(attackersOnSquare)
                pass
            else:
                score -= board.pieces[pieceType] # a piece without protection is one that is essentially lost
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

def overallPieceForkScore(board:betterBoard.BetterBoard, color):
    # ! FLAWED LOGIC WITH ATTACKERS AMOUNT > 1
    return 0
    score = 0
    totalAttackers = []
    for pieceType in [chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN, chess.KING]:
        for square in board.moduleBoard.pieces(pieceType, not color):
            totalAttackers.extend(board.moduleBoard.attackers(color, square))
    c = Counter(totalAttackers)
    for square in c:
        attackersAmount = c[square]
        if attackersAmount > 1:
            # the same piece is attacking multiple pieces
            score += 1
            
    return score

def mobilityScore(board:betterBoard.BetterBoard, color):
    mobility = {
        chess.PAWN:0,
        chess.KNIGHT:0,
        chess.BISHOP:0,
        chess.ROOK:0,
        chess.QUEEN:0,
        chess.KING:0
    }

    for move in board.moduleBoard.legal_moves:
        fromSquare = move.from_square
        toSquare = move.to_square

        pieceType = board.moduleBoard.piece_type_at(fromSquare)

        mobility[pieceType] += 1
    
    # credit to "https://github.com/thorsilver/SpaceDog/blob/master/eval.c" for the mobility weightings
    return 4 * (mobility[chess.KNIGHT] - 4) + 3 * (mobility[chess.BISHOP] - 7) + 4 * (mobility[chess.ROOK] - 7) + 4 * (mobility[chess.QUEEN] - 14)



def pieceSafetyAndStructureScore(board:betterBoard.BetterBoard, color:bool):
    score = 0 

    for pieceType in [chess.PAWN, chess.ROOK, chess.KNIGHT, chess.BISHOP, chess.QUEEN]:
        for square in board.moduleBoard.pieces(pieceType, color):
            attackers = board.moduleBoard.attackers(not color, square)
            defenders = board.moduleBoard.attackers(color, square)
            

            # * pawn structure
            if pieceType == chess.PAWN:
                # ? if pawn is protected (attacked) by any other pawns of its own color
                pawnProtection = any(board.moduleBoard.piece_at(defender).piece_type == chess.PAWN for defender in defenders)
                if pawnProtection:
                    score += 1
                else:
                    score -= 2
            

            # * piece protection score
            if defenders and attackers:
                # ? a piece that is protected and not safe is somewhat bad 
                score -= 1
            elif defenders and not attackers:
                # ? a piece that is protected and safe is good
                score += 1
            elif not defenders and attackers:
                # ? a piece that is not protected and not safe is bad
                score -= 2
            elif not defenders and not attackers:
                # ? a piece that is not protected but safe is still bad
                score -= 2

            
            # * piece fork score
            squaresAttackedByPiece = board.moduleBoard.attacks(square)
            # ? if attacking more than 1 piece, then it is forking some pieces
            # ? only if the piece itself is safe and protected, then reward it 
            if len(squaresAttackedByPiece) >= 2 and not attackers and defenders:
                score += 2 

    return score

            

            



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


if __name__ == '__main__':
    # # test cases

    board = chess.Board('7k/4r3/3n4/8/2qPB3/1P1P4/2P2P2/K7 w - - 0 1')
    modBoard = betterBoard.BetterBoard(board, board.turn)

    # print(pawnStructureScore(modBoard, chess.WHITE))
    # print(overallPieceProtectionScore(modBoard, chess.WHITE))
    # print(pawnStructureScore(modBoard, chess.BLACK))
    # print(overallPieceProtectionScore(modBoard, chess.BLACK))

    # print(passedPawnsScore(modBoard, chess.WHITE))

    # print(mobilityScore(modBoard, board.turn))

    # print(phaseOfGame(modBoard))
    # print(modBoard.phase)

    print(pieceSafetyAndStructureScore(modBoard, board.turn))