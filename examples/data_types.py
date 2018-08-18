#!/usr/bin/env python
# coding=utf-8
"""
tableformatter supports and has been tested with the following tabular data types:
* list of lists or another iterable of iterables
* two-dimensional NumPy arrays
* NumPy record arrays (names as columns)
* pandas.DataFrame
* list or another iterable of arbitrary non-iterable objects (column specifier required)
* list or another iterable of dicts (dict keys iterated through as rows where each key must be a hashable iterable)
* dict of iterables (keys as columns)

This example demonstrates tableformatter working with these data types in the simplest possible manner.
"""
from collections import OrderedDict
import numpy as np
import pandas as pd
import tableformatter as tf

iteralbe_of_iterables = [[1, 2, 3, 4],
                         [5, 6, 7, 8]]
print("Data type: iterable of iterables")
print(iteralbe_of_iterables)
print(tf.generate_table(iteralbe_of_iterables))

np_2d_array = np.array([[1, 2, 3, 4],
                        [5, 6, 7, 8]])
print("Data type: NumPy 2D array")
print(np_2d_array)
print(tf.generate_table(np_2d_array))

np_rec_array = np.rec.array([(1, 2., 'Hello'),
                             (2, 3., "World")],
                            dtype=[('foo', 'i4'), ('bar', 'f4'), ('baz', 'U10')])
print("Data type: Numpy record array")
print(np_rec_array)
print(tf.generate_table(np_rec_array))

d = {'col1': [1, 5], 'col2': [2, 6], 'col3': [3, 7], 'col4': [4, 8]}
od = OrderedDict(sorted(d.items(), key=lambda t: t[0]))
pandas_dataframe = pd.DataFrame(data=od)
print("Data type: Pandas DataFrame")
print(pandas_dataframe)
print(tf.generate_table(pandas_dataframe))

d1 = {1: 'a', 2: 'b', 3: 'c', 4: 'd'}
d2 = {5: 'e', 6: 'f', 7: 'g', 8: 'h'}
iterable_of_dicts = [ OrderedDict(sorted(d1.items(), key=lambda t: t[0])),
                      OrderedDict(sorted(d2.items(), key=lambda t: t[0]))]
print("Data type: iterable of dicts (dict keys iterated through as column values)")
print(iterable_of_dicts)
print(tf.generate_table(iterable_of_dicts))

dict_of_iterables = od
print("Data type: dict of iterables (dict keys iterated through as rows where each key must be a hashable iterable)")
print(dict_of_iterables)
print(tf.generate_table(dict_of_iterables))


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


rows = [MyRowObject(1, 2, 3, 4),
        MyRowObject(5, 6, 7, 8)]
columns = (tf.Column('Col1', attrib='field1'),
           tf.Column('Col2', attrib='field2'),
           tf.Column('Col3', attrib='get_field3'),
           tf.Column('Col4', attrib='field4'))
print("Data type: iterable of arbitrary non-iterable objects")
print(rows)
print(tf.generate_table(rows, columns))
