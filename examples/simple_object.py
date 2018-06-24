#!/usr/bin/env python
# coding=utf-8
"""
Simple demonstration of TableFormatter with a list of objects for the table entries.
This approach requires providing the name of the object attribute to query
for each cell (via attrib='attrib_name').
TableFormatter will check if the attribute is callable. If it is, it wall be called
and the returned result will be displayed for that cell.
"""
from tableformatter import generate_table, FancyGrid, SparseGrid, Column


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


rows = [MyRowObject('A1', 'A2', 'A3', 'A4'),
        MyRowObject('B1', 'B2\nB2\nB2', 'B3', 'B4'),
        MyRowObject('C1', 'C2', 'C3', 'C4'),
        MyRowObject('D1', 'D2', 'D3', 'D4')]


columns = (Column('Col1', attrib='field1'),
           Column('Col2', attrib='field2'),
           Column('Col3', attrib='get_field3'),
           Column('Col4', attrib='field4'))

print("Table with header, AlteratingRowGrid:")
print(generate_table(rows, columns))


print("Table with header, transposed, AlteratingRowGrid:")
print(generate_table(rows, columns, transpose=True))


print("Table with header, transposed, FancyGrid:")
print(generate_table(rows, columns, grid_style=FancyGrid(), transpose=True))

print("Table with header, transposed, SparseGrid:")
print(generate_table(rows, columns, grid_style=SparseGrid(), transpose=True))


columns2 = (Column('Col1', attrib='field3'),
            Column('Col2', attrib='field2'),
            Column('Col3', attrib='field1'),
            Column('Col4', attrib='field4'))


print("Table with header, Columns rearranged")
print(generate_table(rows, columns2))
