def getRandomGameState():
    import chess.pgn
    import random as r
    import chess 
    import io
    with open('startingVariations.txt', 'r') as variationTxt:
        lines = variationTxt.readlines()
        choice = ''
        while not choice.strip():
            choice = r.choice(lines)


        board = chess.Board()

        game = chess.pgn.read_game(io.StringIO(choice))
        return game
    