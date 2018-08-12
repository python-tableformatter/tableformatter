# coding=utf-8
"""
Unit testing the variety of data types supported by tableformatter.
"""
import numpy as np
import pandas as pd
import tableformatter as tf


EXPECTED_BASIC = '''
╔═══╤═══╤═══╤═══╗
║ 1 │ 2 │ 3 │ 4 ║
║ 5 │ 6 │ 7 │ 8 ║
╚═══╧═══╧═══╧═══╝
'''.lstrip('\n')

EXPECTED_WITH_HEADERS = '''
╔══════╤══════╤══════╤══════╗
║ col1 │ col2 │ col3 │ col4 ║
╠══════╪══════╪══════╪══════╣
║ 1    │ 2    │ 3    │ 4    ║
║ 5    │ 6    │ 7    │ 8    ║
╚══════╧══════╧══════╧══════╝
'''.lstrip('\n')

iteralbe_of_iterables = [[1, 2, 3, 4],
                         [5, 6, 7, 8]]
np_2d_array = np.array(iteralbe_of_iterables)
d = {'col1': [1, 5], 'col2': [2, 6], 'col3': [3, 7], 'col4': [4, 8]}
df = pd.DataFrame(data=d)


def test_iterable_of_iterables():
    table = tf.generate_table(iteralbe_of_iterables)
    assert table == EXPECTED_BASIC


def test_numpy_2d_array():
    np_2d_array = np.array(iteralbe_of_iterables)
    table = tf.generate_table(np_2d_array)
    assert table == EXPECTED_BASIC


def test_iterable_of_dicts():
    iterable_of_dicts = [{1: 'a', 2: 'b', 3: 'c', 4: 'd'},
                         {5: 'e', 6: 'f', 7: 'g', 8: 'h'}]
    table = tf.generate_table(iterable_of_dicts)
    assert table == EXPECTED_BASIC


def test_numpy_record_array():
    np_rec_array = np.rec.array([(1, 2., 'Hello'),
                                 (2, 3., "World")],
                                    dtype=[('foo', 'i4'), ('bar', 'f4'), ('baz', 'U10')])
    table = tf.generate_table(np_rec_array)
    expected = '''
╔═════╤═════╤═══════╗
║ foo │ bar │ baz   ║
╠═════╪═════╪═══════╣
║ 1   │ 2.0 │ Hello ║
║ 2   │ 3.0 │ World ║
╚═════╧═════╧═══════╝
'''.lstrip('\n')
    assert table == expected


def test_pandas_dataframe():
    table = tf.generate_table(df)
    assert table == EXPECTED_WITH_HEADERS


def test_dict_of_iterables():
    table = tf.generate_table(d)
    assert table == EXPECTED_WITH_HEADERS


class MyRowObject(object):
    """Simple object to demonstrate using a list of non-iterable objects with TableFormatter"""
    def __init__(self, field1: int, field2: int, field3: int, field4: int):
        self.field1 = field1
        self.field2 = field2
        self._field3 = field3
        self.field4 = field4

    def get_field3(self):
        """Demonstrates accessing object functions"""
        return self._field3


def test_iterable_of_non_iterable_objects():
    rows = [MyRowObject(1, 2, 3, 4),
            MyRowObject(5, 6, 7, 8)]
    columns = (tf.Column('col1', attrib='field1'),
               tf.Column('col2', attrib='field2'),
               tf.Column('col3', attrib='get_field3'),
               tf.Column('col4', attrib='field4'))
    table = tf.generate_table(rows, columns)
    assert table == EXPECTED_WITH_HEADERS
