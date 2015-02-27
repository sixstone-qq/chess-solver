#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Library to resolve chess configurations
"""


class ChessBoard(object):
    """
    Representation of a chess board

    Public attributes:

    * :py:attr:`board` matrix
    * :py:attr:`n_left` the number of free positions and not under attack
    * :py:attr:`n_rows` the number of rows
    * :py:attr:`n_cols` the number of columns
    """
    def __init__(self, n_rows, n_cols):
        self.n_left = n_rows * n_cols
        self.n_rows = n_rows
        self.n_cols = n_cols
        self.board = [[None for j in xrange(n_cols)] for i in xrange(n_rows)]
        self.solution = []
        self._placement_stack = []

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

    def available(self, n_pieces_left):
        """
        :param int n_pieces_left: number of pieces left to place
        :return: the current available positions in a :py:class:`list` of tuples.
        :rtype: :py:class:`list` instance
        """
        available = []
        if self.n_left > 0 or self.n_left >= n_pieces_left:
            for i, row in enumerate(self.board):
                for j, val in enumerate(row):
                    if val is None:
                        available.append((i, j))
        return available

    def is_free(self, piece, row, col):
        """Is this position free for the given :py:class:`Piece`
        """
        return (self.board[row][col] is None and
                all(self.board[i][j] in ('x', None) for (i, j) in piece.attacking_pos(row, col, self) if i >= 0 and j >= 0 and i < self.n_rows and j < self.n_cols))

    def place(self, piece, row, col):
        """Place a :py:class:`Piece` in a (row, col) position
        """
        pos_set = [(i, j, 'x') for (i, j) in piece.attacking_pos(row, col, self) if i >= 0 and j >= 0 and i < self.n_rows and j < self.n_cols and self.board[i][j] is None]
        pos_set.insert(0, (row, col, repr(piece)))
        self._placement_stack.append(len(pos_set))
        self.solution.extend(pos_set)
        for (i, j, s) in pos_set:
            self.board[i][j] = s

    def undo_last_placement(self):
        """Undo the last place call."""
        for _ in xrange(self._placement_stack.pop()):
            (i, j, s) = self.solution.pop()
            self.board[i][j] = None


class Piece(object):
    """General piece.

    Two pieces are equal if they are of the same type. This is
    very useful in set collections.
    """
    def __eq__(self, other):
        return type(self) == type(other)

    def __repr__(self):
        return self.__class__.__name__[0]

    def attacking_pos(self, row, col):
        """
        :returns: the places where the piece can attack given a position
        :rtype: :py:class:`generator` instance
        """
        raise NotImplemented()


class King(Piece):
    """King piece."""
    def attacking_pos(self, row, col, chess_board):
        for i in xrange(row - 1, row + 2):
            for j in xrange(col - 1, col + 2):
                if not (i == row and j == col):
                    yield (i, j)


class Bishop(Piece):
    """Bishop piece."""
    def attacking_pos(self, row, col, chess_board):
        # Diagonals
        n_up = row - col
        n_down = row + col
        for j in xrange(chess_board.n_cols):
            if j != col:
                yield (j + n_up, j)
                yield (n_down - j, j)


class Rook(Piece):
    """Rook piece."""
    def attacking_pos(self, row, col, chess_board):
        for j in xrange(chess_board.n_cols):
            if j != col:
                yield (row, j)
        for i in xrange(chess_board.n_rows):
            if i != row:
                yield (i, col)


class Queen(Rook, Bishop):
    """Queen piece."""
    def attacking_pos(self, row, col, chess_board):
        for bishop_tuple in Bishop.attacking_pos(self, row, col, chess_board):
            yield bishop_tuple  # yield from in python 3.3
        for rook_tuple in Rook.attacking_pos(self, row, col, chess_board):
            yield rook_tuple


class Knight(Piece):
    """Knight piece"""
    def __repr__(self):
        return 'N'  # To avoid King confusion

    def attacking_pos(self, row, col, chess_board):
        yield (row + 2, col + 1)
        yield (row + 2, col - 1)
        yield (row + 1, col + 2)
        yield (row + 1, col - 2)
        yield (row - 2, col + 1)
        yield (row - 2, col - 1)
        yield (row - 1, col + 2)
        yield (row - 1, col - 2)


def lsolve(piece, piece_list, chess_board):
    """Local solution for a given configuration

    :param Piece piece: the current piece to place
    :param tuple piece_list: the remainder pieces to place
    :param chess_board: the current configuration of the chess board
    :type chess_board: :py:class:`ChessBoard`
    :returns: the local solutions
    :rtype: :py:class:`set` of string representation of the solution board
    """
    lsolutions = set()
    for free in chess_board.available(len(piece_list) + 1):
        if chess_board.is_free(piece, free[0], free[1]):
            chess_board.place(piece, free[0], free[1])
            if piece_list:
                head, tail = piece_list[0], piece_list[1:]
                new_lsolutions = lsolve(head, tail, chess_board)
                lsolutions = lsolutions.union(new_lsolutions)
            else:
                lsolutions.add(str(chess_board))
            chess_board.undo_last_placement()
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
    :rtype: :py:class:`set` of string representation of the solution board
    """
    # Set the pieces in relative importance order
    pieces = [Queen()] * n_queens + [Rook()] * n_rooks + [Bishop()] * n_bishops + \
             [Knight()] * n_knights + [King()] * n_kings
    chess_board = ChessBoard(n_rows, n_columns)
    next_piece, piece_list = pieces[0], pieces[1:]
    solutions = lsolve(next_piece, piece_list, chess_board)

    return solutions
