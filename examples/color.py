#!/usr/bin/env python
# coding=utf-8
"""
Simple demonstration of TableFormatter with some colored output.
"""
import tableformatter as tf
from tableformatter import generate_table

try:
    from colorama import Back
    BACK_RESET = Back.RESET
    BACK_GREEN = Back.LIGHTGREEN_EX
    BACK_BLUE = Back.LIGHTBLUE_EX
except ImportError:
    try:
        from colored import bg
        BACK_RESET = bg(0)
        BACK_BLUE = bg(27)
        BACK_GREEN = bg(119)
    except ImportError:
        BACK_RESET = ''
        BACK_BLUE = ''
        BACK_GREEN = ''

rows = [('A1', 'A2', 'A3', 'A4'),
        ('B1', 'B2\nB2\nB2', 'B3', 'B4'),
        ('C1', 'C2', 'C3', 'C4'),
        ('D1', 'D2', 'D3', 'D4')]

columns = ('Col1', 'Col2', 'Col3', 'Col4')

print("Table with colorful alternating rows")
print(generate_table(rows, columns, grid_style=tf.AlternatingRowGrid(BACK_GREEN, BACK_BLUE)))
