"""
This is the main driver file for the chess game. It will be responsible for handling user input and displaying the curretn gameState object.
"""

import pygame as p
from chessEngine import *
from smartMoveFinder import *
from multiprocessing import Process, Queue
import sys

WIDTH = HEIGHT = 512 
DIMENSION = 8   # 8 x 8 squares
SQ_SIZE = HEIGHT // DIMENSION
MAX_FPS = 15   # for animations
IMAGES = {}

def loadImages():
    pieces = ["wp", "wR", "wN", "wB", "wQ", "wK", "bp", "bR", "bN", "bB", "bQ", "bK"]
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))
    # can access an image by saying IMAGES["wP"]


def drawGameState(screen, gs, validMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen, gs, validMoves, sqSelected)

# Draws the squares on the board
def drawBoard(screen):
    global colors
    colors = [p.Color(160, 108, 88), p.Color(255,229,204)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draws the pieces on the board
def drawPieces(screen, gs, validMoves, sqSelected):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = gs.board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

    # Draw dots for valid moves
    if sqSelected:
        for move in validMoves:
            if move.startRow == sqSelected[0] and move.startCol == sqSelected[1]:
                end_square_center = (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2)
                p.draw.circle(screen, (100, 100, 50), end_square_center, SQ_SIZE // 10)


'''
Highlight square selected and moves for piece
'''
def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):
            # Highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)  # Make surface transparent
            s.fill((200, 200, 100, 100))  # Fill with a lighter shade of board color
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            # Highlight moves from that square with a dot
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    end_square_center = (move.endCol * SQ_SIZE + SQ_SIZE // 2, move.endRow * SQ_SIZE + SQ_SIZE // 2)
                    p.draw.circle(screen, (100, 100, 50), end_square_center, SQ_SIZE // 10)  # Draw dot with darker shade

            if gs.inCheck:
                kingRow, kingCol = gs.whiteKingLocation if gs.whiteToMove else gs.blackKingLocation
                if (kingRow, kingCol) == (r, c):
                    p.draw.rect(screen, p.Color("red"), p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE), 3)

'''
Animate move
'''
def animateMove(move, screen, board, clock, validMoves, sqSelected):
    global colors
    coords = []  # list of coordinates that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    distance = max(abs(dR), abs(dC))  # Calculate maximum distance to determine framesPerSquare
    framesPerSquare = 10  # Default frames to move one square

    # Calculate the duration based on the longest distance
    frameCount = framesPerSquare * max(abs(dR), abs(dC))

    for frame in range(frameCount + 1):
        r = move.startRow + dR * frame / frameCount
        c = move.startCol + dC * frame / frameCount
        drawBoard(screen)
        drawPieces(screen, board, validMoves, sqSelected)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isenPassantMove:
                enPassantRow = (move.endRow + 1) if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = p.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Black'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2, HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, p.Color('Gray'))
    screen.blit(textObject, textLocation.move(2, 2))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
    p.display.set_caption('Chess')
    clock = p.time.Clock()
    screen.fill(p.Color("white"))
    gs = GameState()
    validMoves = gs.getValidMoves()
    moveMade = False
    animate = False # flag variable for when we need to animate a move
    loadImages() # only do this once, before the while loop
    running = True
    sqSelected = () # no square is selected, keep track of last click tuple(row, col)
    playerClicks = [] # keep track of player clicks, 2 tuples: [(6, 4), (4, 4)]
    gameOver = False
    playerOne = True # if a human is playing white, then this will be true
    playerTwo = False # if a human is playing black, then this will be true
    AIThinking = False
    moveFinderProcess = None
    moveUndone = False
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
                p.quit()
                sys.exit()
            
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos() # (x, y) location
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE
                    if sqSelected == (row, col): # user clicked the same square twice
                        sqSelected = () # deselect
                        playerClicks = []
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected) # append for both 1st and 2nd click
                    if len(playerClicks) == 2 and humanTurn: # after 2nd click
                        move = Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])
                                moveMade = True
                                animate = True
                                sqSelected = () # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]   
            # key handler

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: # undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
                if e.key == p.K_r:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False #Reset gameFlag
                    if AIThinking:
                        moveFinderProcess.terminate()
                        AIThinking = False
                    moveUndone = True
        
        # AI move finder logic
        if not gameOver and not humanTurn and not moveUndone:
            if not AIThinking:
                AIThinking = True
                print("thinking....")
                returnQueue = Queue() # used to pass data between processes/ threads
                moveFinderProcess = Process(target= findBestMove, args=(gs, validMoves, returnQueue))
                moveFinderProcess.start() # starting the process
                
            if not moveFinderProcess.is_alive():
                print('DOne thinking!!!') 
                AIMove = returnQueue.get()   
                if AIMove is None:
                    AIMove = findRandomMove(validMoves)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False
        
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs, clock, validMoves, sqSelected)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False
            moveUndone = False

        drawGameState(screen, gs, validMoves, sqSelected)
        
        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, "Black wins by checkmate")
            else:
                drawText(screen, "White wins by checkmate")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate")

        clock.tick(MAX_FPS)
        p.display.flip()

if __name__ == "__main__":
    main()