"""
This class is responsible for storing all the information about the current state of a chess game. It will also be responsible for determining the valid moves at the current state. It will also keep a move log.
"""

class GameState():
    def __init__(self):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"],
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'Q': self.getQueenMoves, 'K': self.getKingMoves}
        self.whiteToMove = True
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        # 3 for checks and pins
        self.inCheck = False
        self.pins = []
        self.checks = []
        
        self.checkmate = False
        self.stalemate = False
        self.moveLog = []
        self.enPassantPossible = ()  # coordinates for the square where en passant capture is possible
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]


    # Takes a move as a parameter and executes it (this will not work for castling, pawn promotion and en-passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move) # log the move so we can undo it later
        self.whiteToMove = not self.whiteToMove # swap players

        # update king's location if moved
        if move.pieceMoved == 'wK':
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLocation = (move.endRow, move.endCol)
        
        #if pawn moves twice, next move will be en passant
        #update enPassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2: #only on 2 square pawn advances
            self.enPassantPossible = ((move.startRow + move.endRow) // 2, move.startCol)
        else:
            self.enPassantPossible = ()
        
        #en passant
        if move.isenPassantMove:
            self.board[move.startRow][move.endCol] = '--'
        
        #pawn promotion
        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + 'Q'
        
        #castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: #kingside castle
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1] #moves the rook
                self.board[move.endRow][move.endCol + 1] = '--' #erase old rook
            else: #queenside castle
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2] #moves the rook
                self.board[move.endRow][move.endCol - 2] = '--' #erase old rook
        
        self.enPassantPossibleLog.append(self.enPassantPossible)
        
        #update castling rights - whenever it is a rook or a king move
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    
    def updateCastleRights(self, move):
        '''
        update castling rights whenever it is a rook or a king move
        '''
        # if a rook is captured, update the castleRights
        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == 'bR':
            if move.endRow == 0:
                if move.endCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:
                    self.currentCastlingRight.bks = False

        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:
                    self.currentCastlingRight.bks = False
        
        

    # Undo last move
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove # swap players

            # update king's location if moved
            if move.pieceMoved == 'wK':
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLocation = (move.startRow, move.startCol)
            
            #undo en passant is different
            if move.isenPassantMove:
                self.board[move.endRow][move.endCol] = '--' # leave landing square blank
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            # undo castling rights
            self.castleRightsLog.pop() # get rid of the new castle rights from the move just undone
            self.currentCastlingRight = self.castleRightsLog[-1] # set the current castle rights to the last one in the list

            # update the king's position in castling rights if necessary
            if move.pieceMoved == 'wK':
                self.currentCastlingRight.wks = True
                self.currentCastlingRight.wqs = True
            elif move.pieceMoved == 'bK':
                self.currentCastlingRight.bqs = True
                self.currentCastlingRight.bks = True

            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: #kingside castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1] #moves the rook
                    self.board[move.endRow][move.endCol - 1] = '--' #erase old rook
                else: #queenside castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1] #moves the rook
                    self.board[move.endRow][move.endCol + 1] = '--' #erase old rook

            self.checkmate = False
            self.stalemate = False

    # All moves considering checks
    def getValidMoves(self):
        moves = []
        self.inCheck, self.pins, self.checks = self.checkForPinsAndChecks()
        if self.whiteToMove:
            kingRow, kingCol = self.whiteKingLocation
        else:
            kingRow, kingCol = self.blackKingLocation

        if self.inCheck:
            if len(self.checks) == 1: # only 1 check, block check or move king
                moves = self.getAllPossibleMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]
                checkRow, checkCol = check[0], check[1]
                pieceChecking = self.board[checkRow][checkCol]
                validSquares = []
                if pieceChecking[1] == 'N': # if knight, must capture knight or move king, other pieces can be blocked
                    validSquares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        validSquare = (kingRow + check[2] * i, kingCol + check[3] * i) # check[2] and check[3] are the check directions
                        validSquares.append(validSquare)
                        if validSquare[0] == checkRow and validSquare[1] == checkCol: # once you get to your king, stop
                            break
                # get rid of moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):
                    if moves[i].pieceMoved[1] != 'K': # move doesn't move king so it must block or capture
                        if (moves[i].endRow, moves[i].endCol) not in validSquares: # move doesn't block check or capture piece
                            moves.remove(moves[i])
            else: # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else: # not in check so all moves are fine
            moves = self.getAllPossibleMoves()

            # Include castling moves for white
            if self.whiteToMove:
                if self.currentCastlingRight.wks:
                    self.getKingsideCastleMoves(kingRow, kingCol, moves)
                if self.currentCastlingRight.wqs:
                    self.getQueensideCastleMoves(kingRow, kingCol, moves)
            else: # castling moves for black
                if self.currentCastlingRight.bks:
                    self.getKingsideCastleMoves(kingRow, kingCol, moves)
                if self.currentCastlingRight.bqs:
                    self.getQueensideCastleMoves(kingRow, kingCol, moves)

        if len(moves) == 0:
            if self.inCheck:
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        return moves
    
    # All moves without considering checks
    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # calls appropriate move func based on piece
                    self.moveFunctions[piece](r, c, moves)
        return moves        


    def checkForPinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        inCheck = False
        
        if self.whiteToMove:
            enemyColor = "b"
            allyColor = "w"
            startRow = self.whiteKingLocation[0]
            startCol = self.whiteKingLocation[1]
        else:
            enemyColor = "w"
            allyColor = "b"
            startRow = self.blackKingLocation[0]
            startCol = self.blackKingLocation[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            d = directions[j]
            possiblePin = ()  # reset possible pins
            for i in range(1, 8):
                endRow = startRow + d[0] * i
                endCol = startCol + d[1] * i
                if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] == allyColor and endPiece[1] != "K":
                        if possiblePin == ():  # first allied piece could be pinned
                            possiblePin = (endRow, endCol, d[0], d[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif endPiece[0] == enemyColor:
                        enemyType = endPiece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemyType == "R") or (4 <= j <= 7 and enemyType == "B") or (
                                i == 1 and enemyType == "p" and (
                                (enemyColor == "w" and 6 <= j <= 7) or (enemyColor == "b" and 4 <= j <= 5))) or (
                                enemyType == "Q") or (i == 1 and enemyType == "K"):
                            if possiblePin == ():  # no piece blocking, so check
                                inCheck = True
                                checks.append((endRow, endCol, d[0], d[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possiblePin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knightMoves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knightMoves:
            endRow = startRow + move[0]
            endCol = startCol + move[1]
            if 0 <= endRow <= 7 and 0 <= endCol <= 7:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] == enemyColor and endPiece[1] == "N":  # enemy knight attacking a king
                    inCheck = True
                    checks.append((endRow, endCol, move[0], move[1]))
        return inCheck, pins, checks


    def getPawnMoves(self, row, col, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteToMove:
            moveAmount = -1
            startRow = 6
            enemyColor = "b"
            kingRow, kingCol = self.whiteKingLocation
        else:
            moveAmount = 1
            startRow = 1
            enemyColor = "w"
            kingRow, kingCol = self.blackKingLocation

        if self.board[row + moveAmount][col] == "--":  # 1 square pawn advance
            if not piecePinned or pinDirection == (moveAmount, 0):
                moves.append(Move((row, col), (row + moveAmount, col), self.board))
                if row == startRow and self.board[row + 2 * moveAmount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * moveAmount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piecePinned or pinDirection == (moveAmount, -1):
                if self.board[row + moveAmount][col - 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col - 1), self.board))
                if (row + moveAmount, col - 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            insideRange = range(kingCol + 1, col - 1)
                            outsideRange = range(col + 1, 8)
                        else:  # king right of the pawn
                            insideRange = range(kingCol - 1, col, -1)
                            outsideRange = range(col - 2, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col - 1), self.board, isEnpassantMove=True))
        if col + 1 <= 7:  # capture to the right
            if not piecePinned or pinDirection == (moveAmount, 1):
                if self.board[row + moveAmount][col + 1][0] == enemyColor:
                    moves.append(Move((row, col), (row + moveAmount, col + 1), self.board))
                if (row + moveAmount, col + 1) == self.enPassantPossible:
                    attackingPiece = blockingPiece = False
                    if kingRow == row:
                        if kingCol < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            insideRange = range(kingCol + 1, col)
                            outsideRange = range(col + 2, 8)
                        else:  # king right of the pawn
                            insideRange = range(kingCol - 1, col + 1, -1)
                            outsideRange = range(col - 1, -1, -1)
                        for i in insideRange:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blockingPiece = True
                        for i in outsideRange:
                            square = self.board[row][i]
                            if square[0] == enemyColor and (square[1] == "R" or square[1] == "Q"):
                                attackingPiece = True
                            elif square != "--":
                                blockingPiece = True
                    if not attackingPiece or blockingPiece:
                        moves.append(Move((row, col), (row + moveAmount, col + 1), self.board, isEnpassantMove=True))
            
    def getRookMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8: # on board
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # enemy piece invalid
                            break
                else: # off board
                    break

    def getBishopMoves(self, r, c, moves):
        piecePinned = False
        pinDirection = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                pinDirection = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break
        
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not piecePinned or pinDirection == d or pinDirection == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece == "--": # empty space valid
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                        elif endPiece[0] == enemyColor:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break
                        else: # enemy piece invalid
                            break
                else: # off board
                    break
    
    def getKnightMoves(self, r, c, moves):
        piecePinned = False
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                piecePinned = True
                self.pins.remove(self.pins[i])
                break
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2),
                       (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                if not piecePinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != allyColor: #not ally piece (empty or enemy piece
                        moves.append(Move((r, c), (endRow, endCol), self.board))

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)
    
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        allyColor = 'w' if self.whiteToMove else 'b'
        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: #not ally piece (empty or enemy piece
                    # place king on end square and check for checks
                    if allyColor == 'w':
                        self.whiteKingLocation = (endRow, endCol)
                    else:
                        self.blackKingLocation = (endRow, endCol)
                    inCheck, pins, checks = self.checkForPinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    # place king back on original location
                    if allyColor == 'w':
                        self.whiteKingLocation = (r, c)
                    else:
                        self.blackKingLocation = (r, c)

    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove
        oppMoves = self.getAllPossibleMoves()
        self.whiteToMove = not self.whiteToMove
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False
    
    
    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)
    
    def getKingsideCastleMoves(self, r, c, moves):
        # Check if the king is within the bounds of the board
        if 0 <= r < len(self.board) and 0 <= c < len(self.board[0]):
            # Check if the king is not at the edge of the board
            if c + 2 < len(self.board[0]):
                # Check if the squares for castling are empty
                if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
                    # Check if the squares the king moves through are not under attack
                    if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                        moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))

class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    # maps keys to values
    # key : value
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnpassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.isPawnPromotion = (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7)
        #en passant
        self.isenPassantMove = isEnpassantMove
        if self.isenPassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp'
        
        #castling
        self.isCastleMove = isCastleMove
        
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol
    
    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)
    
    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]