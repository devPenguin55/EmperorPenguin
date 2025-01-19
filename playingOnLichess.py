import chess
import chess.pgn
import emperorPenguin as player
import settings

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import time as t
from bs4 import BeautifulSoup
import requests
import json
import re

def grabLatestFen(lastFen):
    curFen = lastFen
    while lastFen == curFen:
        curFen = driver.find_elements(
            By.CLASS_NAME, 'copyable')[0]
        if curFen:
            curFen = curFen.get_attribute('value')
        else:
            curFen = lastFen
        t.sleep(1)
    return curFen

def seleniumBoardPushUciMove(move):
    pieces = []
    for piece in driver.find_elements(By.CSS_SELECTOR, 'piece'):
        coordDict = piece.location
        pieces.append((piece, coordDict))

    positions = []

    targetSquare = move[2:4]
    for coord in squareCoords:
        if coord in squareCoords:
            if squareCoords[coord] == targetSquare:
                endedCoords = coord

    startPiece = None
    startCoords = None
    for piece, location in pieces:
        location = (location['x'], location['y'])
        square = squareCoords[location]
        # print(square, move)
        if square in move[0:2]:
            startPiece = piece
            startCoords = location
    
    targetElement = driver.find_element(By.CSS_SELECTOR, 'cg-board')
    endCoords = [endedCoords[0], endedCoords[1]]
    endCoords[0] -= startCoords[0]
    endCoords[1] -= startCoords[1]

    actions = ActionChains(driver)
    # print("e=e", startCoords, endedCoords, endCoords, startPiece)
    actions.click_and_hold(startPiece).move_to_element_with_offset(startPiece, endCoords[0], endCoords[1]).release().perform()


if __name__ == '__main__':
    print('starting')

    # game = chess.pgn.Game()
    # node = game

    BOT = False
    useStockfish = False
    turn = True # False -> bot white, True -> bot black

    options = Options()
    options.add_argument("user-data-dir=C:\\Users\\aarav\\AppData\\Local\\Google\\Chrome\\User Data")

    service = Service(executable_path='C:\\Automations\\chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    driver.get('https://lichess.org/analysis')
    # driver.get('https://lichess.org/vLJDB3WO')
    driver.implicitly_wait(1)


    t.sleep(10)


    board = chess.Board()
    for sanMove in [i.text for i in driver.find_elements(By.TAG_NAME, 'kwdb')]:
        board.push_san(sanMove)
    board1 = board.copy()
    p1 = player.Player(board1, chess.WHITE, t=5000)  # playing chess.com bots - make the player be black, flip board to white being on bottom
    p2 = player.Player(board1, chess.BLACK, t=5000)
    

    # basically it only generated the first 2 rows of pieces for black and white (not whole board)
    inputData = ''
    pieces = []
    for piece in driver.find_elements(By.CSS_SELECTOR, 'piece'):
        coordDict = piece.location
        pieces.append((piece, coordDict))
        # print(piece, piece.location)
        inputData += str(piece) + ' ' + str(piece.location) + '\n'

    coordinates = re.findall(r"'x': (\d+), 'y': (\d+)", inputData)
    coordinates = [(int(x), int(y)) for x, y in coordinates]

    # allXs = []
    # allYs = []
    # for x, y in coordinates:
    #     allXs.append(x)
    #     allYs.append(y)
    # allXs = list(set(allXs))
    # allYs = list(set(allYs))
    # allXs.sort()
    # allYs.sort()
    # xGap = allXs[1] - allXs[0]
    # yGap = allYs[1] - allYs[0]
    # firstSquare = (allXs[0], allYs[0])

    # squareCoords = {}
    # for y in range(0, 8):
    #     for x in range(0, 8):
    #         squareCoords[(firstSquare[0]+xGap*x, firstSquare[1]+yGap*y)] = 'abcdefgh'[x]+'87654321'[y]
    # print(squareCoords)

    
    lastFen = board.fen()

    legal_move = True
    while not board.is_game_over(claim_draw=True) and legal_move:
        board_copy = board.copy()
        if turn == True:
            # user turn
            if not BOT:
                if True:
                    curFen = grabLatestFen(lastFen)
                    board.set_fen(curFen)
                else:
                    st = t.time()
                    while True:
                        move = driver.find_element(By.CLASS_NAME, 'a1t').text
                        # print(move)
                        try:
                            board.push_san(move)
                            print('pushed', move)
                            t.sleep(3)  
                            break
                        except:
                            pass
            else:
                if useStockfish:
                    stockfishMove = json.loads(requests.get(f'https://www.stockfish.online/api/s/v2.php?fen={board.fen().replace(' ', '%20')}&depth=3').content)['bestmove'].split(' ')[1]
                    print('STOCKFISH MOVE ->', stockfishMove)
                    driver.find_element(By.CLASS_NAME, 'ready').send_keys(stockfishMove)
                    board.push_uci(stockfishMove)

                    # node = node.add_variation(chess.Move.from_uci(stockfishMove))
                else:
                    move = p2.move(board_copy, timeLeft=60)
                    print(f'Bot move - {move}')
                    board.push(move)
                    # node = node.add_variation(move)
                    move = move.uci()

                    driver.find_element(By.CLASS_NAME, 'ready').send_keys(move)
        else:
            # try:
                move = p1.move(board_copy, timeLeft=60)
                print(f'Bot move - {move}')
                board.push(move)
                # node = node.add_variation(move)
                move = move.uci()

                driver.find_element(By.CLASS_NAME, 'ready').send_keys(move)
                t.sleep(3)
            # except Exception as e:
            #     print(e)
            #     pass  
        # print()
        # print(game)
        # print()
        lastFen = board.fen()
        turn = not turn

        

        t.sleep(1)


    t.sleep(6000 )
    driver.quit()   
