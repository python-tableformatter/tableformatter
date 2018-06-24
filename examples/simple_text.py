#!/usr/bin/env python
# coding=utf-8
"""
Simple demonstration of TableFormatter with a list of tuples as table entries.
TableFormatter will automatically expand the row height to handle multi-line entries.
"""
import tableformatter as tf
from tableformatter import generate_table

rows = [('A1', 'A2', 'A3', 'A4'),
        ('B1', 'B2\nB2\nB2', 'B3', 'B4'),
        ('C1', 'C2', 'C3', 'C4'),
        ('D1', 'D2', 'D3', 'D4')]

columns = ('Col1', 'Col2', 'Col3', 'Col4')

print("Basic Table, default style (AlternatingRowGrid):")
print(generate_table(rows))


print("Basic Table, transposed, default style (AlternatingRowGrid):")
print(generate_table(rows, transpose=True))


print("Basic Table, FancyGrid:")
print(generate_table(rows, grid_style=tf.FancyGrid()))

print("Basic Table, SparseGrid:")
print(generate_table(rows, grid_style=tf.SparseGrid()))

print("Table with header, AlteratingRowGrid:")
print(generate_table(rows, columns))


print("Table with header, transposed, AlteratingRowGrid:")
print(generate_table(rows, columns, transpose=True))


print("Table with header, transposed, FancyGrid:")
print(generate_table(rows, columns, grid_style=tf.FancyGrid(), transpose=True))

print("Table with header, transposed, SparseGrid:")
print(generate_table(rows, columns, grid_style=tf.SparseGrid(), transpose=True))
