#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Library to resolve chess configurations
"""
from copy import deepcopy


class ChessBoard(object):
    """
    Representation of a chess board

    Public attributes:

    * :py:attr:`board` matrix
    * :py:attr:`n_left` the number of free positions and not under attack
    """
    def __init__(self, n_rows, n_cols):
        self.n_left = n_rows * n_cols
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.board = [[None for j in xrange(n_cols)] for i in xrange(n_rows)]

    def take(self, row, col, val):
        """
        Take a position in the chess with `val`.

        :param str val: the str representation of a piece or the 'x' to represent
                        this position is now under attack.
        """
        if (row >= 0 and row < self.n_rows and
           col >= 0 and col < self.n_cols):
            if self.board[row][col] is None:
                self.n_left -= 1
            self.board[row][col] = val
            # else: Out of bounds or already taken

    def val(self, row, col):
        """
        Get the current value of a `(row, col)`.

        :returns: the current piece in str representation. `None` if it is free or 'x' if it is under attack
        :rtype: str
        """
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
        """Dump to standard out the current chess board"""
        print str(self)

    def available(self, n_pieces_left):
        """
        :param int n_pieces_left: number of pieces left to place
        :return: the current available positions in a generator.
                 Each time is called, a :py:class:`tuple` is returned.
        :rtype: generator
        """
        if self.n_left > 0 or self.n_left >= n_pieces_left:
            for i, row in enumerate(self.board):
                for j, val in enumerate(row):
                    if val is None:
                        yield (i, j)


class Piece(object):
    """General piece.

    Two pieces are equal if they are of the same type. This is
    very useful in set collections.
    """
    def __eq__(self, other):
        return type(self) == type(other)

    def __repr__(self):
        return self.__class__.__name__[0]

    def available_in(self, row, col, chess_board):
        """Check if a piece can be placed in that position.

        :param piece: the piece to place
        :type piece: :py:class:`Piece`
        :returns: True if the position is free and not under attack
        """
        raise NotImplemented()

    def place(self, row, col, chess_board):
        """Place a piece in the chessboard. It checks if the position
        to place it is free and not under attack.

        :param chess_board: the chess board to check and update.
        :type chess_board: :py:class:`ChessBoard`
        :returns: True if the piece was placed, false otherwise
        """
        raise NotImplemented()


class King(Piece):
    """King piece."""
    def available_in(self, row, col, chess_board):
        return (chess_board.val(row, col) is None and
                chess_board.val(row - 1, col - 1) in ('x', None) and
                chess_board.val(row - 1, col) in ('x', None) and
                chess_board.val(row - 1, col + 1) in ('x', None) and
                chess_board.val(row, col - 1) in ('x', None) and
                chess_board.val(row, col + 1) in ('x', None) and
                chess_board.val(row + 1, col - 1) in ('x', None) and
                chess_board.val(row + 1, col) in ('x', None) and
                chess_board.val(row + 1, col + 1) in ('x', None))

    def place(self, row, col, chess_board):
        chess_board.take(row, col, repr(self))
        chess_board.take(row - 1, col - 1, 'x')
        chess_board.take(row - 1, col, 'x')
        chess_board.take(row - 1, col + 1, 'x')
        chess_board.take(row, col - 1, 'x')
        chess_board.take(row, col + 1, 'x')
        chess_board.take(row + 1, col - 1, 'x')
        chess_board.take(row + 1, col, 'x')
        chess_board.take(row + 1, col + 1, 'x')


class Queen(Piece):
    """Queen piece."""
    def available_in(self, row, col, chess_board):
        # Diagonals
        n_up = row - col
        n_down = row + col
        return (chess_board.val(row, col) is None and
                all(chess_board.val(i + n_up, i) in ('x', None) and
                    chess_board.val(n_down - i, i) in ('x', None) and
                    chess_board.val(row, i) in ('x', None) for i in xrange(chess_board.n_cols) if i != col) and
                all(chess_board.val(j, col) in ('x', None) for j in xrange(chess_board.n_rows)))

    def place(self, row, col, chess_board):
        # Diagonals
        n_up = row - col
        n_down = row + col
        for i in xrange(chess_board.n_cols):
            chess_board.take(i + n_up, i, 'x')
            chess_board.take(n_down - i, i, 'x')
            chess_board.take(row, i, 'x')
        for j in xrange(chess_board.n_rows):
            chess_board.take(j, col, 'x')
        chess_board.take(row, col, repr(self))


class Bishop(Piece):
    """Bishop piece."""
    def available_in(self, row, col, chess_board):
        # Diagonals
        n_up = row - col
        n_down = row + col
        return (chess_board.val(row, col) is None and
                all([chess_board.val(i + n_up, i) in ('x', None) and
                     chess_board.val(n_down - i, i) in ('x', None) for i in xrange(chess_board.n_cols) if i != col]))

    def place(self, row, col, chess_board):
        # Diagonals
        n_up = row - col
        n_down = row + col
        for i in xrange(chess_board.n_cols):
            chess_board.take(i + n_up, i, 'x')
            chess_board.take(n_down - i, i, 'x')
        chess_board.take(row, col, repr(self))


class Rook(Piece):
    """Rook piece."""
    def available_in(self, row, col, chess_board):
        return (all([chess_board.val(row, j) in ('x', None) for j in xrange(chess_board.n_cols)] +
                    [chess_board.val(i, col) in ('x', None) for i in xrange(chess_board.n_rows)]))

    def place(self, row, col, chess_board):
        for j in xrange(0, chess_board.n_cols):
            chess_board.take(row, j, 'x')
        for i in xrange(0, chess_board.n_rows):
            chess_board.take(i, col, 'x')
        chess_board.take(row, col, repr(self))


class Knight(Piece):
    """Knight piece"""
    def __repr__(self):
        return 'N'  # To avoid King confusion

    def available_in(self, row, col, chess_board):
        return (chess_board.val(row, col) is None and
                chess_board.val(row + 2, col + 1) in ('x', None) and
                chess_board.val(row + 2, col - 1) in ('x', None) and
                chess_board.val(row + 1, col + 2) in ('x', None) and
                chess_board.val(row + 1, col - 2) in ('x', None) and
                chess_board.val(row - 2, col + 1) in ('x', None) and
                chess_board.val(row - 2, col - 1) in ('x', None) and
                chess_board.val(row - 1, col + 2) in ('x', None) and
                chess_board.val(row - 1, col - 2) in ('x', None))

    def place(self, row, col, chess_board):
        chess_board.take(row, col, repr(self))
        chess_board.take(row + 2, col + 1, 'x')
        chess_board.take(row + 2, col - 1, 'x')
        chess_board.take(row + 1, col + 2, 'x')
        chess_board.take(row + 1, col - 2, 'x')
        chess_board.take(row - 2, col + 1, 'x')
        chess_board.take(row - 2, col - 1, 'x')
        chess_board.take(row - 1, col + 2, 'x')
        chess_board.take(row - 1, col - 2, 'x')


def lsolve(piece, piece_list, chess_board):
    """Local solution for a given configuration

    :param Piece piece: the current piece to place
    :param tuple piece_list: the remainder pieces to place
    :param chess_board: the current configuration of the chess board
    :type chess_board: :py:class:`ChessBoard`
    :returns: the local solutions
    :rtype: :py:class:`frozenset` of :py:class:`ChessBoard` objects
    """
    lsolutions = frozenset()
    for free in chess_board.available(len(piece_list) + 1):
        if piece.available_in(free[0], free[1], chess_board):
            updated_chess_board = deepcopy(chess_board)
            piece.place(free[0], free[1], updated_chess_board)
            if piece_list:
                head, tail = piece_list[0], piece_list[1:]
                new_lsolutions = lsolve(head, tail, updated_chess_board)
                lsolutions = lsolutions.union(new_lsolutions)
            else:
                lsolutions = frozenset((updated_chess_board,))
    return lsolutions


def solve(n_rows, n_columns, n_kings=0, n_queens=0, n_bishops=0, n_rooks=0, n_knights=0):
    """Place in a board of *n_rows* x *n_columns* with the pieces set as arguments
    all the possible unique configurations where none of the pieces is in a
    position to take any of the others.

    :param int n_rows: the number of rows of the chess board
    :param int n_columns: the number of columns of the chess board
    :param int n_kings: the number of King pieces
    :param int n_queens: the number of Queen pieces
    :param int n_bishops: the number of Bishop pieces
    :param int n_rooks: the number of Rook pieces
    :param int n_knights: the number of Knight pieces
    :return: all the possible configurations
    :rtype: :py:class:`frozenset` of :py:class:`ChessBoard` objects
    """
    # Set the pieces in relative importance order
    pieces = [Queen()] * n_queens + [Rook()] * n_rooks + [Bishop()] * n_bishops + \
             [Knight()] * n_knights + [King()] * n_kings
    chess_board = ChessBoard(n_rows, n_columns)
    next_piece, piece_list = pieces[0], pieces[1:]
    solutions = lsolve(next_piece, piece_list, chess_board)

    return solutions
