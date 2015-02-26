#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHON_ARGCOMPLETE_OK
import argparse
from chess import solve
import re


try:
    import argcomplete
    __autocomplete = True
except:
    __autocomplete = False


def board(string):
    match = re.match(r'(\d+)x(\d+)', string)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    else:
        raise argparse.ArgumentTypeError("Board size format is: MxN")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Chess pieces puzzle solver.",
                                     epilog="If any piece is set with a value, other default values are ignored.")
    parser.add_argument('--board', '-B', type=board,
                        default='7x7', help="Set the board size using format MxN. Default: 7x7")
    parser.add_argument('--kings', '-k', type=int,
                        help="Number of kings in the chess board. Default: 2")
    parser.add_argument('--queens', '-q', type=int,
                        help="Number of queens in the chess board. Default: 2")
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
    pieces_names = ('kings', 'queens', 'bishops', 'rooks', 'knights')
    if all([getattr(args, arg_name) is None for arg_name in pieces_names]):
        # Number of solutions: 1322707 (188m)
        args.kings = 2
        args.queens = 2
        args.bishops = 2
        args.rooks = 0
        args.knights = 1
    else:
        # Transform None to 0 for non-defined arguments
        for arg_name in pieces_names:
            if getattr(args, arg_name) is None:
                setattr(args, arg_name, 0)

    sols = solve(n_rows=args.board[0], n_columns=args.board[1],
                 n_kings=args.kings, n_queens=args.queens,
                 n_bishops=args.bishops, n_rooks=args.rooks, n_knights=args.knights)
    for sol in sols:
        sol.dump()
    print "\nNumber of solutions: {}".format(len(sols))
