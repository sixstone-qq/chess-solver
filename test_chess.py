#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Unit tests over chess library
"""
from chess import solve
from unittest import TestCase
import unittest


class SolveTestCase(TestCase):

    def test_2_kings_1_rook_3x3(self):
        sols = solve(3, 3, n_kings=2, n_rooks=1)
        self.assertEqual(len(sols), 4)
        first_sol = iter(sols).next()
        self.assertEqual(first_sol.val(2, 0), 'K')
        self.assertEqual(first_sol.val(0, 1), 'R')
        self.assertEqual(first_sol.val(2, 2), 'K')

    def test_2_rooks_4_Knights_4x4(self):
        sols = solve(4, 4, n_rooks=2, n_knights=4)
        self.assertEqual(len(sols), 8)

    def test_2_bishops_3_queens_6x4(self):
        sols = solve(6, 4, n_bishops=2, n_queens=3)
        self.assertEqual(len(sols), 36)

    def test_5_queens_5x5(self):
        sols = solve(5, 5, n_queens=5)
        self.assertEqual(len(sols), 10)


if __name__ == '__main__':
    unittest.main()
