# BoardGame.py

# Somewhat incomplete BoardGame class.
# For example, no way to win.  No score.  No reset.
# Still, a practical example of inheritance!  :-)

import os
import pickle
import random
from argparse import ArgumentParser
from tkinter import *

from Animation import Animation

###########################################
# Utility functions
###########################################

def make2dList(rows, cols):
    a=[]
    for row in range(rows): a += [[0]*cols]
    return a

###########################################
# BoardGame class
###########################################

class BoardGame(Animation):
    def getCurrentPlayer(self):
        return self.currentPlayer

    def changePlayers(self):
        self.currentPlayer += 1
        if (self.currentPlayer > self.totalPlayers):
            self.currentPlayer = 1

    def cellPressed(self, row, col):
        print("cell pressed: (%d, %d)" % (row, col))
        self.board[row][col] = self.getCurrentPlayer()
        self.changePlayers()

    def cellClear(self, row, col):
        print("clearing: (%d, %d)" % (row, col))
        self.board[row][col] = 0

    def mousePressed(self, event):
        if (self.isOnBoard(event.x, event.y)):
            (row, col) = self.getCellFromLocation(event.x, event.y)
            self.cellPressed(row, col)

    def secondaryMousePressed(self, event):
        if (self.isOnBoard(event.x, event.y)):
            (row, col) = self.getCellFromLocation(event.x, event.y)
            self.cellClear(row, col)

    def redrawAll(self):
        self.drawTitle()
        self.drawPlayersTurn()
        self.drawBoard()

    def drawTitle(self):
        self.canvas.create_text(self.width//2, self.titleMargin//2, text=self.title, font=self.titleFont, fill=self.titleFill)
        self.canvas.create_line(0, self.titleMargin, self.width, self.titleMargin, fill=self.titleFill)

    def drawPlayersTurn(self):
        msg = "Player %d's turn" % self.currentPlayer
        self.canvas.create_text(self.boardMargin, self.titleMargin//2, text=msg, font=self.playersTurnFont, anchor=W)

    def drawBoard(self):
        for row in range(self.rows):
            for col in range(self.cols):
                self.drawCell(row, col)

    def drawCell(self, row, col):
        (x0, y0, x1, y1) = self.getCellBounds(row, col)
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.cellBorderColor)
        self.drawCellContents(row, col, self.getCellContentsBounds(row, col))

    def drawCellContents(self, row, col, bounds):
        (x0, y0, x1, y1) = bounds
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=self.cellBackgroundColor)
        color = self.getCellColor(row, col)
        if (color != None):
            if (self.fillCellsWithCircles == True):
                (cx, cy) = ((x0+x1)//2, (y0+y1)//2)
                r = int(0.4*self.cellSize)
                self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color)
            else:
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color)

    def getCellColor(self, row, col):
        value = self.board[row][col]
        if (type(value) == str):
            # string values should be color names, like "blue", etc...
            return value
        elif (type(value) == int):
            assert(-1 < value < len(self.cellColors))
            return self.cellColors[value]
        else:
            raise Exception("Unknown board value: %r" % value)

    def isOnBoard(self, x, y):
        (boardX0, boardY0, boardX1, boardY1) = self.getBoardBounds()
        return ((x >= boardX0) and (x <= boardX1) and
                (y >= boardY0) and (y <= boardY1))

    def getCellFromLocation(self, x, y):
        (boardX0, boardY0, boardX1, boardY1) = self.getBoardBounds()
        row = (y - boardY0) // self.cellSize
        col = (x - boardX0) // self.cellSize
        return (row, col)

    def getBoardBounds(self):
        boardX0 = self.boardMargin
        boardX1 = self.width - self.boardMargin
        boardY0 = self.titleMargin + self.boardMargin
        boardY1 = self.height - self.boardMargin
        return (boardX0, boardY0, boardX1, boardY1)

    def getCellBounds(self, row, col):
        (boardX0, boardY0, boardX1, boardY1) = self.getBoardBounds()
        cellX0 = boardX0 + col*self.cellSize
        cellX1 = cellX0 + self.cellSize
        cellY0 = boardY0 + row*self.cellSize
        cellY1 = cellY0 + self.cellSize
        return (cellX0, cellY0, cellX1, cellY1)

    def getCellContentsBounds(self, row, col):
        (cellX0, cellY0, cellX1, cellY1) = self.getCellBounds(row, col)
        cm = self.cellMargin
        return (cellX0+cm, cellY0+cm, cellX1-cm, cellY1-cm)

    def __init__(self, title, rows, cols, cellSize=30):
        self.title = title
        self.rows = rows
        self.cols = cols
        self.cellSize = cellSize
        self.titleFont = "Arial 14 bold"
        self.playersTurnFont = "Arial 10"
        self.titleMargin = 40
        self.titleFill = "blue"
        self.boardMargin = 10
        self.cellMargin = 0
        self.board = make2dList(rows, cols)
        self.cellBorderColor = "black"
        self.cellBackgroundColor = "green"
        self.cellColors = [None, "black", "white"]
        self.fillCellsWithCircles = True
        self.totalPlayers = 2
        self.currentPlayer = 1

    def run(self):
        width = self.cols*self.cellSize + 2*self.boardMargin
        height = (self.rows * self.cellSize) + self.titleMargin + 2*self.boardMargin
        super(BoardGame, self).run(width, height)

###########################################
# GoTrust class
###########################################

class GoTrust(BoardGame):
    backup_fname = "go_board.pickle"

    def __init__(self, rows, cols, cellSize=30):
        title = "Board Game Test"
        super(GoTrust, self).__init__(title, rows, cols, cellSize)
        self.board[0][0] = "red"
        self.board[1][1] = 0
        self.board[2][2] = 1
        self.board[3][3] = 2

    def keyPressed(self, event):
        if event.keysym == "s":
            self.save()

    def save(self):
        save_fname = GoTrust.backup_fname

        # keep previous game state; helpful for viewing last move
        if os.path.isfile(save_fname):
            fmt = "backup existing save file {} --> {}"
            backup_save_fname = save_fname + ".bak"
            print(fmt.format(save_fname, backup_save_fname))
            os.rename(save_fname, backup_save_fname)

        print("saving board state to", save_fname)
        with open(save_fname, "wb") as f:
            # protocol 2 to support Python >= 2.3
            pickle.dump(self.board, f, protocol=2)

    def load(self):
        with open(GoTrust.backup_fname, "rb") as f:
            self.board = pickle.load(f)

def getargs():
    ap = ArgumentParser("A Barebones Go game")
    ap.add_argument("-r", "--restore", help="restore game state from file")
    return ap.parse_args()

if (__name__ == "__main__"):
    args = getargs()

    game = GoTrust(10, 15)
    if args.restore:
        game.load()
    game.run()
