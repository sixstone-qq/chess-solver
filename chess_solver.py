#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import argparse
from copy import deepcopy
from itertools import permutations
import re


try:
    import argcomplete
    __autocomplete = True
except:
    __autocomplete = False


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
        if self.n_left == 0:
            return []
        else:
            available = []
            for i, row in enumerate(self.board):
                for j, val in enumerate(row):
                    if val is None:
                        available.append((i, j))
            return available


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


def solve(n_rows, n_columns, n_kings, n_bishops, n_rooks, n_knights):
    solutions = set()
    # Set the pieces in relative importance order
    pieces = [Rook()] * n_rooks + [Bishop()] * n_bishops + [Knight()] * n_knights + \
             [King()] * n_kings
    for piece in set(pieces):
        for row in xrange(n_rows):
            for col in xrange(n_columns):
                # Empty board
                other_pieces = deepcopy(pieces)
                other_pieces.remove(piece)
                for p in set(permutations(other_pieces)):
                    chess_board = ChessBoard(n_rows, n_columns)
                    placed = piece.place(row, col, chess_board)
                    found = False
                    for other in p:
                        # Find the right place
                        found = False
                        for free in chess_board.available():
                            placed = other.place(free[0], free[1], chess_board)
                            if placed:
                                found = True
                                break
                        if not found:
                            # No viable branch
                            break
                    if found:
                        solutions.add(chess_board)

    return solutions


def board(string):
    match = re.match(r'(\d+)x(\d+)', string)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    else:
        raise argparse.ArgumentTypeError("Board size format is: MxN")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chess pieces puzzle solver",
                                     epilog="If any piece is set different from default other defaults are ignored.")
    parser.add_argument('--board', '-B', type=board,
                        default='7x7', help="Set the board size using format MxN. Default: 7x7")
    parser.add_argument('--kings', '-k', type=int,
                        help="Number of kings in the chess board. Default: 2")
    parser.add_argument('--bishops', '-b', type=int,
                        help="Number of bishops in the chess board. Default: 2")
    parser.add_argument('--rooks', '-r', type=int,
                        help="Number of rooks in the chess board. Default: 0")
    parser.add_argument('--knights', '-n', type=int,
                        help="Number of knights in the chess board. Default: 1")

    if __autocomplete:
            argcomplete.autocomplete(parser)

    args = parser.parse_args()

    # if all piece arguments are None, then set the defaults
    pieces_names = ('kings', 'bishops', 'rooks', 'knights')
    if all([getattr(args, arg_name) is None for arg_name in pieces_names]):
            args.kings = 2
            args.bishops = 2
            args.rooks = 0
            args.knights = 1
    else:
            # Transform None to 0 for non-defined arguments
            for arg_name in pieces_names:
                if getattr(args, arg_name) is None:
                    setattr(args, arg_name, 0)

    sols = solve(args.board[0], args.board[1], args.kings, args.bishops, args.rooks, args.knights)
    for sol in sols:
        sol.dump()
    print "\nNumber of solutions: {}".format(len(sols))
