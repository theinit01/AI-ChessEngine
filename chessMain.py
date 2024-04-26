"""
This is the main driver file for the chess game. It will be responsible for handling user input and displaying the curretn gameState object.
"""

import pygame as p
from chessEngine import *

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
    drawPieces(screen, gs)

# Draws the squares on the board
def drawBoard(screen):
    global colors
    colors = [p.Color(160, 108, 88), p.Color(255,229,204)]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((row + col) % 2)]
            p.draw.rect(screen, color, p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Draws the pieces on the board
def drawPieces(screen, gs):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = gs.board[row][col]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

def main():
    p.init()
    screen = p.display.set_mode((WIDTH, HEIGHT))
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
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            
            # mouse handler
            elif e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos() # (x, y) location
                col = location[0] // SQ_SIZE
                row = location[1] // SQ_SIZE
                if sqSelected == (row, col): # user clicked the same square twice
                    sqSelected = () # deselect
                    playerClicks = []
                else:
                    sqSelected = (row, col)
                    playerClicks.append(sqSelected) # append for both 1st and 2nd click
                if len(playerClicks) == 2: # after 2nd click
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
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
                    animate = False
                if e.key == p.K_r:
                    gs = GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
        
        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs, clock)
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs, validMoves, sqSelected)
        clock.tick(MAX_FPS)
        p.display.flip()

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
'''
Animate move
'''
def animateMove(move, screen, board, clock):
    global colors
    coords = [] # list of coordinates that the animation will move through
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 8 # frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
                screen.blit(IMAGES[move.pieceCaptured], endSquare)
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)
main()