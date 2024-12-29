from multiprocessing import Manager, Pool
import random as r
import chess
import transpositionTable

def work(tt, state, flag, depth, value):
    tt.store(state, flag, depth, value)
   

def randomBoard():
    board = chess.Board()
    
    for _ in range(r.randint(20, 50)):
        legal_moves = list(board.legal_moves)
        if legal_moves:
            move = r.choice(legal_moves)
            board.push(move)
    
    return board

if __name__ == '__main__':
    with Manager() as manager:
        sharedDict = manager.dict()
        tt = transpositionTable.TT(sharedDict)
        
        with Pool(10) as pool:
            pool.starmap(work, [(tt, randomBoard(), 1, r.randint(0, i), r.randint(-100, i*50)) for i in range(10)])
        print(tt.table)