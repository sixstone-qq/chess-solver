#!/usr/bin/env python
# -*- coding: utf-8 -*-
from copy import deepcopy


class ChessBoard(object):
    def __init__(self, n_rows, n_cols):
        self.n_left = n_rows * n_cols
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.board = [[None for j in xrange(n_cols)] for i in xrange(n_rows)]

    def take(self, row, col, val):
        if (row >= 0 and row < self.n_rows and
           col >= 0 and col < self.n_cols and
           self.board[row][col] is None):
            self.board[row][col] = val
            self.n_left -= 1
            # else: Out of bounds or already taken

    def val(self, row, col):
        if (row >= 0 and row < self.n_rows and
           col >= 0 and col < self.n_cols):
            return self.board[row][col]
        else:
            return None

    def __repr__(self):
        return str(self)

    def __str__(self):
        ret = ""
        for row in self.board:
            ret += ' '.join(' ' if j is None else str(j) for j in row) + "\n"
        return ret

    def __eq__(self, other):
        if (self.n_rows == other.n_rows and
           self.n_cols == other.n_cols):
            return all((self.board[i][j] == other.board[i][j] for j in xrange(self.n_cols) for i in xrange(self.n_rows)))
        else:
            return False

    def __hash__(self):
        return hash(tuple(hash(tuple(row)) for row in self.board))

    def dump(self):
        print str(self)

    def available(self):
        if self.n_left > 0:
            for i, row in enumerate(self.board):
                for j, val in enumerate(row):
                    if val is None:
                        yield (i, j)


class Piece(object):
    def __eq__(self, other):
        return type(self) == type(other)

    def __repr__(self):
        return self.__class__.__name__[0]


class King(Piece):
    def place(self, row, col, chess_board):
        if (chess_board.val(row, col) is None and
           chess_board.val(row - 1, col - 1) in ('x', None) and
           chess_board.val(row - 1, col) in ('x', None) and
           chess_board.val(row - 1, col + 1) in ('x', None) and
           chess_board.val(row, col - 1) in ('x', None) and
           chess_board.val(row, col + 1) in ('x', None) and
           chess_board.val(row + 1, col - 1) in ('x', None) and
           chess_board.val(row + 1, col) in ('x', None) and
           chess_board.val(row + 1, col + 1) in ('x', None)):
            chess_board.take(row, col, 'K')
            chess_board.take(row - 1, col - 1, 'x')
            chess_board.take(row - 1, col, 'x')
            chess_board.take(row - 1, col + 1, 'x')
            chess_board.take(row, col - 1, 'x')
            chess_board.take(row, col + 1, 'x')
            chess_board.take(row + 1, col - 1, 'x')
            chess_board.take(row + 1, col, 'x')
            chess_board.take(row + 1, col + 1, 'x')
            return True
        else:
            return False


class Queen(Piece):
    def place(self, row, col, chess_board):
        # Diagonals
        n_up = row - col
        n_down = row + col
        if (chess_board.val(row, col) is None and
           all(chess_board.val(i + n_up, i) in ('x', None) and
               chess_board.val(n_down - i, i) in ('x', None) and
               chess_board.val(row, i) in ('x', None) for i in xrange(chess_board.n_cols) if i != col) and
           all(chess_board.val(j, col) in ('x', None) for j in xrange(chess_board.n_rows))):
            chess_board.take(row, col, 'Q')
            for i in xrange(chess_board.n_cols):
                if i != col:
                    chess_board.take(i + n_up, i, 'x')
                    chess_board.take(n_down - i, i, 'x')
                    chess_board.take(row, i, 'x')
            for j in xrange(chess_board.n_rows):
                if j != row:
                    chess_board.take(j, col, 'x')
            return True
        else:
            return False


class Bishop(Piece):
    def place(self, row, col, chess_board):
        # Diagonals
        n_up = row - col
        n_down = row + col
        if (chess_board.val(row, col) is None and
           all([chess_board.val(i + n_up, i) in ('x', None) and
                chess_board.val(n_down - i, i) in ('x', None) for i in xrange(chess_board.n_cols) if i != col])):
            chess_board.take(row, col, 'B')
            for i in xrange(chess_board.n_cols):
                if i != col:
                    chess_board.take(i + n_up, i, 'x')
                    chess_board.take(n_down - i, i, 'x')
            return True
        else:
            return False


class Rook(Piece):
    def place(self, row, col, chess_board):
        if (all([chess_board.val(row, j) in ('x', None) for j in xrange(chess_board.n_cols)] +
                [chess_board.val(i, col) in ('x', None) for i in xrange(chess_board.n_rows)])):
                chess_board.take(row, col, 'R')
                for j in xrange(0, chess_board.n_cols):
                    if j != col and chess_board.val(row, j) is None:
                        chess_board.take(row, j, 'x')
                for i in xrange(0, chess_board.n_rows):
                    if i != row and chess_board.val(i, col) is None:
                        chess_board.take(i, col, 'x')
                return True
        else:
                return False


class Knight(Piece):
    def __repr__(self):
        return 'N'  # To avoid King confusion

    def place(self, row, col, chess_board):
        if (chess_board.val(row, col) is None and
           chess_board.val(row + 2, col + 1) in ('x', None) and
           chess_board.val(row + 2, col - 1) in ('x', None) and
           chess_board.val(row + 1, col + 2) in ('x', None) and
           chess_board.val(row + 1, col - 2) in ('x', None) and
           chess_board.val(row - 2, col + 1) in ('x', None) and
           chess_board.val(row - 2, col - 1) in ('x', None) and
           chess_board.val(row - 1, col + 2) in ('x', None) and
           chess_board.val(row - 1, col - 2) in ('x', None)):
            chess_board.take(row, col, 'N')
            chess_board.take(row + 2, col + 1, 'x')
            chess_board.take(row + 2, col - 1, 'x')
            chess_board.take(row + 1, col + 2, 'x')
            chess_board.take(row + 1, col - 2, 'x')
            chess_board.take(row - 2, col + 1, 'x')
            chess_board.take(row - 2, col - 1, 'x')
            chess_board.take(row - 1, col + 2, 'x')
            chess_board.take(row - 1, col - 2, 'x')
            return True
        else:
            return False


def lsolve(piece, piece_list, chess_board):
    lsolutions = frozenset()
    for free in chess_board.available():
        updated_chess_board = deepcopy(chess_board)
        placed = piece.place(free[0], free[1], updated_chess_board)
        if placed:
            if piece_list:
                head, tail = piece_list[0], piece_list[1:]
                new_lsolutions = lsolve(head, tail, deepcopy(updated_chess_board))
                lsolutions = lsolutions.union(new_lsolutions)
            else:
                lsolutions = frozenset((updated_chess_board,))
    return lsolutions


def solve(n_rows, n_columns, n_kings, n_queens, n_bishops, n_rooks, n_knights):
    # Set the pieces in relative importance order
    pieces = [Queen()] * n_queens + [Rook()] * n_rooks + [Bishop()] * n_bishops \
             + [Knight()] * n_knights + [King()] * n_kings
    chess_board = ChessBoard(n_rows, n_columns)
    next_piece, piece_list = pieces[0], pieces[1:]
    solutions = lsolve(next_piece, piece_list, chess_board)

    return solutions
