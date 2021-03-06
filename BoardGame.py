##
# @file BoardGame.py
# @brief Somewhat incomplete BoardGame class.
# @author cwee
#
# @details For example, no way to win.  No score.  No reset.
#          Still, a practical example of inheritance!  :-)
# @bug When starting a new game, if Notifications=yes, game crashes 'cause
#      there isn't a save file to check.

import os
import pickle
import pprint
import random
from argparse import ArgumentParser
from configparser import ConfigParser
from tkinter import *
from threading import Timer

from Animation import Animation
from sync_file import WebDAVFsync

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
        bgColor = self.getCellBackgroundColor(row, col)
        self.canvas.create_rectangle(x0, y0, x1, y1, fill=bgColor)
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

    def getCellBackgroundColor(self, row, col):
        return self.cellBackgroundColor

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
    backup_fname = "go_trust.pickle"
    pp = pprint.PrettyPrinter(compact=True)

    def __init__(self, dimensions, title, file_sync):
        rows, cols = dimensions
        cellSize = 30
        super(GoTrust, self).__init__(title, rows, cols, cellSize)
        self.moves = [] # list of tuple(player, row, col)
        self.game_sync = file_sync
        self.thread = None

    def cellPressed(self, row, col):
        player = self.getCurrentPlayer()
        self.moves.append((player, row, col))
        super().cellPressed(row, col)

    def cellClear(self, row, col):
        self.moves.append((0, row, col))
        super().cellClear(row, col)

    ##
    # @brief Last move for each player should have its cell background a
    # slightly different color.
    def getCellBackgroundColor(self, row, col):
        coord = (row, col)

        for player in range(1, self.totalPlayers + 1):
            for move_player, move_row, move_col in reversed(self.moves):
                move_coord = (move_row, move_col)

                # last move this player made (account for moves undone)
                if move_player == player == self.board[move_row][move_col]:
                    if move_coord == coord:
                        return "#ADFF2F"  # HTML greenyellow
                    break

        return super().getCellBackgroundColor(row, col)

    def keyPressed(self, event):
        if event.keysym == "s":
            self.save()
        elif event.keysym == "m":
            self.print_moves()
        elif event.keysym == "n":
            self.popup_update(hash("test"))

    def print_moves(self):
        GoTrust.pp.pprint(self.moves)

    def save(self):
        save_fname = GoTrust.backup_fname

        # keep previous game state; helpful for viewing last move
        if os.path.isfile(save_fname):
            fmt = "backup existing save file {} --> {}"
            backup_save_fname = save_fname + ".bak"
            print(fmt.format(save_fname, backup_save_fname))
            os.rename(save_fname, backup_save_fname)

        print("saving game state to", save_fname),
        state = {
            "board": self.board,
            "moves": self.moves,
        }
        with open(save_fname, "wb") as f:
            # protocol 2 to support Python >= 2.3
            pickle.dump(state, f, protocol=2)

        self.game_sync.upload()
        print('Finished.')

    def load(self):
        self.game_sync.download()

        with open(GoTrust.backup_fname, "rb") as f:
            state = pickle.load(f)

        self.board = state["board"]
        self.moves = state["moves"]

        last_player = None
        for player, _, _ in reversed(self.moves):
            # find last valid player (ignore cleared cells)
            if (1 <= player <= self.totalPlayers):
                last_player = player
                break
        self.currentPlayer = last_player
        self.changePlayers()

    ##
    # @details Layout is 3x3 grid.
    def popup_update(self, new_state):
        top = Toplevel()
        top.title("Go")

        # row 0
        msg_str = "Game state has changed!"
        msg = Message(top, aspect=1000, text=msg_str, pady=10)
        msg.grid(row=0, columnspan=3)

        # row 1
        msg = Message(top, aspect=1000, text="Remind me in", anchor=E)
        msg.grid(row=1, column=0)

        snooze_options = (15, 30, 60)
        selected = StringVar(top)
        selected.set(snooze_options[0])
        w = OptionMenu(top, selected, *snooze_options)
        w.grid(row=1, column=1)

        msg = Message(top, text="min", anchor=W)
        msg.grid(row=1, column=2)

        # row 2
        def update():
            self.load()
            top.destroy()
        button = Button(top, text="Update local state", command=update)
        button.grid(row=2, column=0, padx=10, pady=10)

        def remind_later():
            delay = float(selected.get()) * 60  # convert min to sec
            self.thread = Timer(delay, lambda: self.popup_update(new_state))
            self.thread.start()
            top.destroy()
        button = Button(top, text="Remind me later", command=remind_later)
        button.grid(row=2, column=1, columnspan=2, padx=10, pady=10)

    def exit(self):
        if self.thread is not None:
            self.thread.cancel()

def getargs():
    ap = ArgumentParser("A Barebones Go game")
    ap.add_argument("--config", default="config.ini",
                    help="config file path")
    ap.add_argument("-r", "--restore", action="store_true",
                    help="restore game state from network")
    return ap.parse_args()


def main():
    args = getargs()

    cfg = ConfigParser()
    cfg.read(args.config)

    dav_sync = WebDAVFsync(
        cfg["sync"]["URL"],
        GoTrust.backup_fname,
        cfg["sync"]["Username"],
        cfg["sync"]["Password"],
        cfg["sync"].getfloat("Interval"),
    )
    game = GoTrust(dimensions=(13, 13), title="Go", file_sync=dav_sync)

    if cfg["sync"].getboolean("Notifications"):
        dav_sync.set_callback(game.popup_update)

    if args.restore:
        game.load()
    game.run()

    game.exit()
    dav_sync.stop()


if __name__ == "__main__":
    main()
