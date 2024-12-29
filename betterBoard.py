import chess
import copy
import settings

class BetterBoard:
    def __init__(self, startingBoard:chess.Board, color):
        self.moduleBoard = startingBoard
        self.color = color

        self.pieces = {
            chess.KING: 200,
            chess.QUEEN: 90,
            chess.ROOK: 50,
            chess.BISHOP: 30,
            chess.KNIGHT: 30,
            chess.PAWN: 10,
            'k': 200,
            'q': 90,
            'r': 50,
            'b': 30,
            'n': 30,
            'p': 10,
        }


        self.OPENING = 0
        self.MIDDLEGAME = 1
        self.ENDGAME = 2

        maxPieces = 32 # each piece of each color
        minPieces = 2 # 2 kings of each color

        boardPieces = 0
        for color in [chess.WHITE, chess.BLACK]:
            for pieceType in [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
                boardPieces += len(startingBoard.pieces(pieceType, color))

        gameProgressionScore = (maxPieces - boardPieces) / (maxPieces - minPieces)

        if gameProgressionScore < settings.openingThreshold:
            self.phase = self.OPENING
        elif gameProgressionScore < settings.middleGameThreshold:
            self.phase = self.MIDDLEGAME
        else:
            self.phase = self.ENDGAME


        self.pawns = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5, -10,  0,  0, -10, -5,  5,
            5, 10, 10, -20, -20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        self.knights = [
            -50, -40, -30, -30, -30, -30, -40, -50,
            -40, -20,  0,  0,  0,  0, -20, -40,
            -30,  0, 10, 15, 15, 10,  0, -30,
            -30,  5, 15, 20, 20, 15,  5, -30,
            -30,  0, 15, 20, 20, 15,  0, -30,
            -30,  5, 10, 15, 15, 10,  5, -30,
            -40, -20,  0,  5,  5,  0, -20, -40,
            -50, -40, -30, -30, -30, -30, -40, -50,
        ]
        self.bishops = [
            -20, -10, -10, -10, -10, -10, -10, -20,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  5, 10, 10,  5,  0, -10,
            -10,  5,  5, 10, 10,  5,  5, -10,
            -10,  0, 10, 10, 10, 10,  0, -10,
            -10, 10, 10, 10, 10, 10, 10, -10,
            -10,  5,  0,  0,  0,  0,  5, -10,
            -20, -10, -10, -10, -10, -10, -10, -20,
        ]
        self.rooks = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]
        self.queen = [
            -20, -10, -10, -5, -5, -10, -10, -20,
            -10,  0,  0,  0,  0,  0,  0, -10,
            -10,  0,  5,  5,  5,  5,  0, -10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0, -10,
            -10,  0,  5,  0,  0,  0,  0, -10,
            -20, -10, -10, -5, -5, -10, -10, -20
        ]
        self.kingMiddleGame = [
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -30, -40, -40, -50, -50, -40, -40, -30,
            -20, -30, -30, -40, -40, -30, -30, -20,
            -10, -20, -20, -20, -20, -20, -20, -10,
            20, 20,  0,  0,  0,  0, 20, 20,
            20, 30, 10,  0,  0, 10, 30, 20
        ]
        self.kingEndGame = [
            -50, -40, -30, -20, -20, -30, -40, -50,
            -30, -20, -10,  0,  0, -10, -20, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 30, 40, 40, 30, -10, -30,
            -30, -10, 20, 30, 30, 20, -10, -30,
            -30, -30,  0,  0,  0,  0, -30, -30,
            -50, -30, -30, -30, -30, -30, -30, -50
        ]

        self.mappedPieces = {
            'p': self.pawns,
            'n': self.knights,
            'b': self.bishops,
            'r': self.rooks,
            'q': self.queen,
            'k': self.kingMiddleGame  # adjust later to have both tables for kind IMPORTANT
        }
        if self.color == chess.BLACK:
            # black will invert the tables
            self.pawns.reverse()
            self.bishops.reverse()
            self.knights.reverse()
            self.queen.reverse()
            self.rooks.reverse()
            self.kingMiddleGame.reverse()
            self.kingEndGame.reverse()

        self.pieceTypesFromString = {
            'p':chess.PAWN,
            'n':chess.KNIGHT, 
            'k':chess.KING,
            'b':chess.BISHOP,
            'r':chess.ROOK,
            'q':chess.QUEEN
        }
        self.typesOfPieces = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.QUEEN, chess.KING, chess.ROOK]

        self.whitePieceCount = sum([len(startingBoard.pieces(pieceType, chess.WHITE))*self.pieces[pieceType] for pieceType in self.typesOfPieces])
        self.blackPiecesCount = sum([len(startingBoard.pieces(pieceType, chess.BLACK))*self.pieces[pieceType] for pieceType in self.typesOfPieces])

        if self.color == chess.WHITE:
            self.material = self.whitePieceCount - self.blackPiecesCount
        else:
            self.material = self.blackPiecesCount - self.whitePieceCount 

        self.materialAlteringMoveStack = []

        self.locationScoreAlteringMoveStack = []
        self.locationScore = 0

        self.recalculateEval()

        

    
    def recalculateEval(self):
        '''
        rough eval calculation - not real, just estimate from material and positions
        '''
        # material calculation
        self.whitePieceCount = sum([len(self.moduleBoard.pieces(pieceType, chess.WHITE))*self.pieces[pieceType] for pieceType in self.typesOfPieces])
        self.blackPiecesCount = sum([len(self.moduleBoard.pieces(pieceType, chess.BLACK))*self.pieces[pieceType] for pieceType in self.typesOfPieces])

        if self.color == chess.WHITE:
            self.material = self.whitePieceCount - self.blackPiecesCount
        else:
            self.material = self.blackPiecesCount - self.whitePieceCount 

        # location calculation
        pieceMap = self.moduleBoard.piece_map()

        def transformIndex(index):
            # get row and column
            row = index // 8
            col = index % 8

            # get the new row
            newRow = 7 - row

            # find new index
            newIndex = newRow * 8 + col

            return newIndex

        self.locationScore = 0
        for index in pieceMap:
            piece, index = str(pieceMap[index]), index
    
            if self.color == chess.WHITE and piece == piece.lower():
                side = -1
            elif self.color == chess.BLACK and piece == piece.upper():
                side = -1
            else:
                side = 1

            # pieceChessType = self.stringToPiece[piece.lower()]
            table = self.mappedPieces[piece.lower()]
            self.locationScore += table[transformIndex(index)] * side

        # recalculate phase
        maxPieces = 32 # each piece of each color
        minPieces = 2 # 2 kings of each color

        boardPieces = 0
        for color in [chess.WHITE, chess.BLACK]:
            for pieceType in [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
                boardPieces += len(self.moduleBoard.pieces(pieceType, color))

        gameProgressionScore = (maxPieces - boardPieces) / (maxPieces - minPieces)

        if gameProgressionScore < settings.openingThreshold:
            self.phase = self.OPENING
        elif gameProgressionScore < settings.middleGameThreshold:
            self.phase = self.MIDDLEGAME
        else:
            self.phase = self.ENDGAME

    def transformIndex(self, index):
        # get row and column
        row = index // 8
        col = index % 8

        # get the new row
        newRow = 7 - row

        # find new index
        newIndex = newRow * 8 + col

        return newIndex

        

    def setColor(self, color):
        self.color = color
        self.moduleBoard.turn = color

        self.recalculateEval()


    def push(self, move):
        if move == chess.Move.null():
            self.moduleBoard.push(move)
            self.locationScoreAlteringMoveStack.append(0)
            self.materialAlteringMoveStack.append(0)
            return

        # grab the start piece and convert it to a string for future dictionary lookups
        startPiece = self.moduleBoard.piece_at(move.from_square)
        startPieceString = str(startPiece).lower()

        endPiece = self.moduleBoard.piece_at(move.to_square)

        finalAdjustLocationScore = 0

        # handles the updating of the material from a perspective of the color of the board initialized
        if endPiece and self.moduleBoard.is_capture(move):

            recalculatePhase = True
            # get the final piece that is getting captured
            
            endPieceString = str(endPiece).lower()

            # figure out how the material gets updated based on the things figured out above
            value = self.pieces[endPieceString]
            
            if startPiece.color != self.color:
                value *= -1
            
            # update the material and the material altering move stack
            self.material += value
            self.materialAlteringMoveStack.append(value)  

            ########### location score updating
            # if a piece gets captured, its location score should be removed from the score
            capturedPieceTable = self.mappedPieces[endPieceString]
            
            if self.color != startPiece.color:
                side = -1
            else:
                side = 1  

            finalAdjustLocationScore += capturedPieceTable[self.transformIndex(move.to_square)]*side
        else:
            recalculatePhase = False

            # no capture means no change in material
            self.materialAlteringMoveStack.append(0)

        ########  subtract the old piece scores of the current piece being moved
           
        
        table = self.mappedPieces[startPieceString]

        foundPieces = self.moduleBoard.pieces(self.pieceTypesFromString[startPieceString], self.moduleBoard.turn)
        for i in foundPieces: 
            if self.color != startPiece.color:
                side = -1
            else:
                side = 1  
            finalAdjustLocationScore -= table[self.transformIndex(i)]*side
        
        #########  push the move
        self.moduleBoard.push(move)
        #########  get the new piece scores of the current piece that got moved

        foundPieces = self.moduleBoard.pieces(self.pieceTypesFromString[startPieceString], not self.moduleBoard.turn)
        for i in foundPieces:   
            if self.color != startPiece.color:
                side = -1
            else:
                side = 1   
            finalAdjustLocationScore += table[self.transformIndex(i)]*side

        
        # update the location score and location altering move stack 
        self.locationScore += finalAdjustLocationScore
        self.locationScoreAlteringMoveStack.append(finalAdjustLocationScore)


        if recalculatePhase:
            # recalculate phase
            maxPieces = 32 # each piece of each color
            minPieces = 2 # 2 kings of each color

            boardPieces = 0
            for color in [chess.WHITE, chess.BLACK]:
                for pieceType in [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
                    boardPieces += len(self.moduleBoard.pieces(pieceType, color))

            gameProgressionScore = (maxPieces - boardPieces) / (maxPieces - minPieces)

            if gameProgressionScore < settings.openingThreshold:
                if self.phase == self.OPENING:
                    self.phase = self.OPENING
            elif gameProgressionScore < settings.middleGameThreshold:
                if self.phase == self.OPENING:
                    self.phase = self.MIDDLEGAME
            else:
                if self.phase == self.MIDDLEGAME:
                    self.phase = self.ENDGAME
        
    
    def pop(self):
        materialChange = self.materialAlteringMoveStack.pop()
        self.material -= materialChange
        self.locationScore -= self.locationScoreAlteringMoveStack.pop()

        self.moduleBoard.pop()

        if materialChange:
            # recalculate phase
            maxPieces = 32 # each piece of each color
            minPieces = 2 # 2 kings of each color

            boardPieces = 0
            for color in [chess.WHITE, chess.BLACK]:
                for pieceType in [chess.KING, chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN]:
                    boardPieces += len(self.moduleBoard.pieces(pieceType, color))

            gameProgressionScore = (maxPieces - boardPieces) / (maxPieces - minPieces)

            if gameProgressionScore < settings.openingThreshold:
                self.phase = self.OPENING
            elif gameProgressionScore < settings.middleGameThreshold:
                self.phase = self.MIDDLEGAME
            else:
                self.phase = self.ENDGAME

        
    
    def update(self, newBoard:chess.Board):
        '''
        Strictly for when a new move comes into the engine when making a move to have the board updated
        '''
        self.moduleBoard = newBoard.copy()
        
        self.recalculateEval()

    def print(self):
        print(self.moduleBoard, end='\n\n')
    
    def copy(self):
        return copy.deepcopy(self)
    