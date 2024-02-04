with open('whiteBook.txt', "w") as whiteBook:
    with open('blackBook.txt', "w") as blackBook:
        whiteBook.truncate(0)
        blackBook.truncate(0)
        whiteBook.seek(0)
        blackBook.seek(0)

        with open('bigBookMoves.txt', 'r') as f:
            print('starting')
            
            for line in f.readlines()[1:]:
                moves = line.split(' ')
                white = []
                black = []
                turn = 0
                for move in moves:
                    if move:
                        if turn == 0:
                            white.append(move)
                        else:
                            black.append(move)
                        turn = (turn + 1) % 2
                        
                    else:
                        # hit a empty string, stop
                        break

                if white and black:
                    whiteBook.write(" ".join(white).replace('\n', '')+'\n')
                    blackBook.write(" ".join(black).replace('\n', '')+'\n')