#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_slippy_sqlite_generator
----------------------------------

Tests for `slippy_sqlite_generator` module.
"""


import sys
import unittest
from slippy_sqlite_generator import slippy_sqlite_generator


class TestSlippy_generator(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_process(self):
        slippySqliteGenerator = slippy_sqlite_generator.SlippySqliteGenerator(
            # r'C:\Users\Blair\Documents\Locus\Saline\walkingmap.jpg',
            # r'Saline.sqlitedb'
            r'C:\Users\Blair\Documents\Workspace\Locus\Everglades\Everglades_600dpi.png',
            r'Everglades.sqlitedb'
        )
        slippySqliteGenerator.process()
