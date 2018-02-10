#!/usr/bin/python3 

from PIL import Image
import getSave

BOARD_BORDER = 50
SPACE_SIZE = 150
SPACE_BORDER = 10


class TicTacToe():
    def __init__(self):
        self.board = [None, None, None, \
                      None, None, None, \
                      None, None, None]
       
        self.WAYS_TO_WIN = ((0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6))
        self.bg = Image.open('./board.png')
        self.x = Image.open('./cross.png')
        self.o = Image.open('./naught.png')

        self.syms = {'X': self.x, 'O': self.o}

    def place(self, pos, sym):
        """ pos is an index into `self.board`
        sym is either 'X' or 'O'
        """

        if not pos >= 0 or not pos < len(self.board):
            raise IllegalMoveError(pos, "Out of bounds")

        if not self.board[pos]:
            self.board[pos] = sym
        else:
            raise IllegalMoveError(pos, "Already taken")

    def render(self):
        """Renders the state of the board and returns it as a PIL image."""

        board_render = self.bg.copy()

        board = [self.board[y*3:y*3+3] for y in range(3)] # convert the board to a 2d string

        for y,row in enumerate(board):
            for x,mark in enumerate(row):
                if mark:
                    upper_left = self.__pos_to_im_coords(x,y)
                    board_render.paste(self.syms[mark], upper_left, mask=self.syms[mark])

        return board_render

    def __pos_to_im_coords(self, x,y):
        """converts x,y into the upper left corner of a board place"""

        return tuple([BOARD_BORDER + SPACE_BORDER + p * SPACE_SIZE for p in (x,y)])

    def getWinner(self):
        """retrieves the winning piece or declares there to be none so far"""
        for i in range(len(self.WAYS_TO_WIN)):
            if self.board[self.WAYS_TO_WIN[i][0]] == self.board[self.WAYS_TO_WIN[i][1]] == self.board[self.WAYS_TO_WIN[i][2]] and self.board[self.WAYS_TO_WIN[i][0]] != None:
                return self.board[self.WAYS_TO_WIN[i][0]]
        return None

class IllegalMoveError(Exception):
    """Raised when a move is made which is illegal

    Attributes:
        pos: the position of the illegal move
        message: explains what rule was broken
    """
    def __init__(self, pos, message):
        self.pos = pos
        self.message = message

