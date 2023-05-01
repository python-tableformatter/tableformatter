# coding=utf-8
"""
Unit testing the variety of data types supported by tableformatter.
"""
from collections import OrderedDict
from typing import Iterator

import tableformatter as tablefmt


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
d = {'col1': [1, 5], 'col2': [2, 6], 'col3': [3, 7], 'col4': [4, 8]}
od = OrderedDict(sorted(d.items(), key=lambda t: t[0]))


def test_iterable_of_iterables():
    table = tablefmt.generate_table(iteralbe_of_iterables)
    assert table == EXPECTED_BASIC


def test_iterable_of_dicts():
    d1 = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
    d2 = {5: 'e', 6: 'f', 7: 'g', 8: 'h'}
    iterable_of_dicts = [OrderedDict(sorted(d1.items(), key=lambda t: t[0])),
                         OrderedDict(sorted(d2.items(), key=lambda t: t[0]))]
    table = tablefmt.generate_table(iterable_of_dicts)
    assert table == EXPECTED_BASIC


def test_dict_of_iterables():
    table = tablefmt.generate_table(od)
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
    columns = (tablefmt.Column('col1', attrib='field1'),
               tablefmt.Column('col2', attrib='field2'),
               tablefmt.Column('col3', attrib='get_field3'),
               tablefmt.Column('col4', attrib='field4'))
    table = tablefmt.generate_table(rows, columns)
    assert table == EXPECTED_WITH_HEADERS


class NonIndexableRowObject:
    def __init__(self, field1: int, field2: int, field3: int, field4: int):
        self.field1 = field1
        self.field2 = field2
        self._field3 = field3
        self.field4 = field4

    @property
    def field3(self) -> int:
        return self._field3

    def __getitem__(self, key: str) -> int:
        if key == 'field1':
            return self.field1
        elif key == 'field2':
            return self.field2
        elif key == 'field3':
            return self.field3
        elif key == 'field4':
            return self.field4
        else:
            raise KeyError('not a valid field')

    def __len__(self) -> int:
        return 2

    def __iter__(self) -> Iterator[int]:
        return iter((self.field1, self.field2, self._field3, self.field4))


def test_iterable_of_non_indexable_iterables():
    rows = [NonIndexableRowObject(1, 2, 3, 4),
            NonIndexableRowObject(5, 6, 7, 8)]
    columns = (tablefmt.Column('col1', attrib='field1'),
               tablefmt.Column('col2', attrib='field2'),
               tablefmt.Column('col3', attrib='field3'),
               tablefmt.Column('col4', attrib='field4'))
    table = tablefmt.generate_table(rows, columns)
    assert table == EXPECTED_WITH_HEADERS


try:
    import numpy as np
except ImportError:
    pass
else:
    np_2d_array = np.array(iteralbe_of_iterables)

    def test_numpy_2d_array():
        table = tablefmt.generate_table(np_2d_array)
        assert table == EXPECTED_BASIC

    def test_numpy_record_array():
        np_rec_array = np.rec.array([(1, 2., 'Hello'),
                                     (2, 3., "World")],
                                    dtype=[('foo', 'i4'), ('bar', 'f4'), ('baz', 'U10')])
        table = tablefmt.generate_table(np_rec_array)
        expected = '''
╔═════╤═════╤═══════╗
║ foo │ bar │ baz   ║
╠═════╪═════╪═══════╣
║ 1   │ 2.0 │ Hello ║
║ 2   │ 3.0 │ World ║
╚═════╧═════╧═══════╝
'''.lstrip('\n')
        assert table == expected

try:
    import pandas as pd
except ImportError:
    pass
else:
    df = pd.DataFrame(data=od)

    def test_pandas_dataframe():
        table = tablefmt.generate_table(df)
        assert table == EXPECTED_WITH_HEADERS
