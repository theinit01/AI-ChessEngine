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


def drawGameState(screen, gs):
    drawBoard(screen)
    drawPieces(screen, gs)

# Draws the squares on the board
def drawBoard(screen):
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
                    if move in validMoves:
                        gs.makeMove(move)
                        moveMade = True
                        sqSelected = () # reset user clicks
                        playerClicks = []
                    else:
                        playerClicks = [sqSelected]   
            # key handler

            elif e.type == p.KEYDOWN:
                if e.key == p.K_z:
                    gs.undoMove()
                    moveMade = True
        
        if moveMade:
            validMoves = gs.getValidMoves()
            moveMade = False

        drawGameState(screen, gs)
        clock.tick(MAX_FPS)
        p.display.flip()
main()