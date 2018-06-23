# coding=utf-8
"""
Unit testing of tableformatter with simple cases
- with a list of tuples as table entries
- using a list of objects for the table entries
"""
import pytest

import tableformatter as tf

# Make the test results reproducible regardless of what color libraries are installed
tf.TableColors.set_color_library('none')

WITH_HEADER = '╔══════╤══════╤══════╤══════╗\n║ Col1 │ Col2 │ Col3 │ Col4 ║\n╠══════╪══════╪══════╪══════╣\n║ A1   │ A2   │ A3   │ A4   ║\n║ B1   │ B2   │ B3   │ B4   ║\n║      │ B2   │      │      ║\n║      │ B2   │      │      ║\n║ C1   │ C2   │ C3   │ C4   ║\n║ D1   │ D2   │ D3   │ D4   ║\n╚══════╧══════╧══════╧══════╝\n'
HEADER_TRANSPOSED = '╔══════╦════╤════╤════╤════╗\n║ Col1 ║ A1 │ B1 │ C1 │ D1 ║\n║ Col2 ║ A2 │ B2 │ C2 │ D2 ║\n║      ║    │ B2 │    │    ║\n║      ║    │ B2 │    │    ║\n║ Col3 ║ A3 │ B3 │ C3 │ D3 ║\n║ Col4 ║ A4 │ B4 │ C4 │ D4 ║\n╚══════╩════╧════╧════╧════╝\n'


@pytest.fixture
def rows():
    rows = [('A1', 'A2', 'A3', 'A4'),
            ('B1', 'B2\nB2\nB2', 'B3', 'B4'),
            ('C1', 'C2', 'C3', 'C4'),
            ('D1', 'D2', 'D3', 'D4')]
    return rows

@pytest.fixture
def cols():
    columns = ('Col1', 'Col2', 'Col3', 'Col4')
    return columns

def test_basic_table(rows):
    expected = '╔════╤════╤════╤════╗\n║ A1 │ A2 │ A3 │ A4 ║\n║ B1 │ B2 │ B3 │ B4 ║\n║    │ B2 │    │    ║\n║    │ B2 │    │    ║\n║ C1 │ C2 │ C3 │ C4 ║\n║ D1 │ D2 │ D3 │ D4 ║\n╚════╧════╧════╧════╝\n'
    table = tf.generate_table(rows)
    assert table == expected

def test_basic_transposed(rows):
    expected = '╔════╤════╤════╤════╗\n║ A1 │ B1 │ C1 │ D1 ║\n║ A2 │ B2 │ C2 │ D2 ║\n║    │ B2 │    │    ║\n║    │ B2 │    │    ║\n║ A3 │ B3 │ C3 │ D3 ║\n║ A4 │ B4 │ C4 │ D4 ║\n╚════╧════╧════╧════╝\n'
    table = tf.generate_table(rows, transpose=True)
    assert table == expected

def test_basic_fancy_grid(rows):
    expected = '╔════╤════╤════╤════╗\n║ A1 │ A2 │ A3 │ A4 ║\n╟────┼────┼────┼────╢\n║ B1 │ B2 │ B3 │ B4 ║\n║    │ B2 │    │    ║\n║    │ B2 │    │    ║\n╟────┼────┼────┼────╢\n║ C1 │ C2 │ C3 │ C4 ║\n╟────┼────┼────┼────╢\n║ D1 │ D2 │ D3 │ D4 ║\n╚════╧════╧════╧════╝\n'
    table = tf.generate_table(rows, grid_style=tf.FancyGrid)
    assert table == expected

def test_basic_sparse_grid(rows):
    expected = ' A1  A2  A3  A4 \n B1  B2  B3  B4 \n     B2         \n     B2         \n C1  C2  C3  C4 \n D1  D2  D3  D4 \n                \n'
    table = tf.generate_table(rows, grid_style=tf.SparseGrid)
    assert table == expected

def test_table_with_header(rows, cols):
    table = tf.generate_table(rows, cols)
    assert table == WITH_HEADER

def test_table_with_header_transposed(rows, cols):
    table = tf.generate_table(rows, cols, transpose=True)
    assert table == HEADER_TRANSPOSED

def test_table_with_header_transposed_fancy(rows, cols):
    expected = '╔══════╦════╤════╤════╤════╗\n║ Col1 ║ A1 │ B1 │ C1 │ D1 ║\n╟──────╫────┼────┼────┼────╢\n║ Col2 ║ A2 │ B2 │ C2 │ D2 ║\n║      ║    │ B2 │    │    ║\n║      ║    │ B2 │    │    ║\n╟──────╫────┼────┼────┼────╢\n║ Col3 ║ A3 │ B3 │ C3 │ D3 ║\n╟──────╫────┼────┼────┼────╢\n║ Col4 ║ A4 │ B4 │ C4 │ D4 ║\n╚══════╩════╧════╧════╧════╝\n'
    table = tf.generate_table(rows, cols, grid_style=tf.FancyGrid, transpose=True)
    assert table == expected

def test_table_with_header_transposed_sparse(rows, cols):
    expected = ' Col1  A1  B1  C1  D1 \n Col2  A2  B2  C2  D2 \n           B2         \n           B2         \n Col3  A3  B3  C3  D3 \n Col4  A4  B4  C4  D4 \n                      \n'
    table = tf.generate_table(rows, cols, grid_style=tf.SparseGrid, transpose=True)
    assert table == expected


class MyRowObject(object):
    """Simple object to demonstrate using a list of objects with TableFormatter"""
    def __init__(self, field1: str, field2: str, field3: str, field4: str):
        self.field1 = field1
        self.field2 = field2
        self._field3 = field3
        self.field4 = field4

    def get_field3(self):
        """Demonstrates accessing object functions"""
        return self._field3

@pytest.fixture
def obj_rows():
    r = [MyRowObject('A1', 'A2', 'A3', 'A4'),
         MyRowObject('B1', 'B2\nB2\nB2', 'B3', 'B4'),
         MyRowObject('C1', 'C2', 'C3', 'C4'),
         MyRowObject('D1', 'D2', 'D3', 'D4')]
    return r


@pytest.fixture
def obj_cols():
    columns = (tf.Column('Col1', attrib='field1'),
               tf.Column('Col2', attrib='field2'),
               tf.Column('Col3', attrib='get_field3'),
               tf.Column('Col4', attrib='field4'))
    return columns

def test_object_table_with_header(obj_rows, obj_cols):
    table = tf.generate_table(obj_rows, obj_cols)
    assert table == WITH_HEADER

def test_object_table_transposed(obj_rows, obj_cols):
    table = tf.generate_table(obj_rows, obj_cols, transpose=True)
    assert table == HEADER_TRANSPOSED

def test_object_table_fancy_grid(obj_rows, obj_cols):
    expected = '╔══════╤══════╤══════╤══════╗\n║ Col1 │ Col2 │ Col3 │ Col4 ║\n╠══════╪══════╪══════╪══════╣\n║ A1   │ A2   │ A3   │ A4   ║\n╟──────┼──────┼──────┼──────╢\n║ B1   │ B2   │ B3   │ B4   ║\n║      │ B2   │      │      ║\n║      │ B2   │      │      ║\n╟──────┼──────┼──────┼──────╢\n║ C1   │ C2   │ C3   │ C4   ║\n╟──────┼──────┼──────┼──────╢\n║ D1   │ D2   │ D3   │ D4   ║\n╚══════╧══════╧══════╧══════╝\n'
    table = tf.generate_table(obj_rows, obj_cols, grid_style=tf.FancyGrid)
    assert table == expected

def test_object_table_sparse_grid(obj_rows, obj_cols):
    expected = ' A1  A2  A3  A4 \n B1  B2  B3  B4 \n     B2         \n     B2         \n C1  C2  C3  C4 \n D1  D2  D3  D4 \n                \n'
    table = tf.generate_table(obj_rows, obj_cols, grid_style=tf.SparseGrid)
    assert table == expected

def test_object_table_columns_rearranged(obj_rows):
    cols2 = (tf.Column('Col1', attrib='field3'),
             tf.Column('Col2', attrib='field2'),
             tf.Column('Col3', attrib='field1'),
             tf.Column('Col4', attrib='field4'))
    expected = '╔══════╤══════╤══════╤══════╗\n║ Col1 │ Col2 │ Col3 │ Col4 ║\n╠══════╪══════╪══════╪══════╣\n║      │ A2   │ A1   │ A4   ║\n║      │ B2   │ B1   │ B4   ║\n║      │ B2   │      │      ║\n║      │ B2   │      │      ║\n║      │ C2   │ C1   │ C4   ║\n║      │ D2   │ D1   │ D4   ║\n╚══════╧══════╧══════╧══════╝\n'
    table = tf.generate_table(obj_rows, cols2)
    assert table == expected




