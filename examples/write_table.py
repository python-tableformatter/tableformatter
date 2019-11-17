#!/usr/bin/env python3
# coding=utf-8
import tableformatter as tf
from tableformatter import generate_table

rows = [('A1', 'A2', 'A3', 'A4'),
        ('B1', 'B2\nB2\nB2', 'B3', 'B4'),
        ('C1', 'C2', 'C3', 'C4'),
        ('D1', 'D2', 'D3', 'D4')]

columns = ('Col1', 'Col2', 'Col3', 'Col4')

tf.TableColors.set_color_library('None')
with open('table_none.txt', mode='w') as outfile:
    print(generate_table(rows, columns, grid_style=tf.FancyGrid()), file=outfile)

tf.TableColors.set_color_library('colorama')
with open('table_colorama.txt', mode='w') as outfile:
    print(generate_table(rows, columns, grid_style=tf.FancyGrid()), file=outfile)

tf.TableColors.set_color_library('colored')
with open('table_colored.txt', mode='w') as outfile:
    print(generate_table(rows, columns, grid_style=tf.FancyGrid()), file=outfile)
