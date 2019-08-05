#!/usr/bin/env python
# coding=utf-8
"""
Simple demonstration of TableFormatter with a list of dicts for the table entries.
This approach requires providing the dictionary key to query
for each cell (via attrib='attrib_name').
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

KEY1 = "Key1"
KEY2 = "Key2"
KEY3 = "Key3"
KEY4 = "Key4"

rows = [{KEY1:'A1', KEY2:'A2', KEY3:'A3', KEY4:'A4'},
        {KEY1:'B1', KEY2:'B2\nB2\nB2', KEY3:'B3', KEY4:'B4'},
        {KEY1:'C1', KEY2:'C2', KEY3:'C3', KEY4:'C4'},
        {KEY1:'D1', KEY2:'D2', KEY3:'D3', KEY4:'D4'}]


columns = (Column('Col1', attrib=KEY1),
           Column('Col2', attrib=KEY2),
           Column('Col3', attrib=KEY3),
           Column('Col4', attrib=KEY4))

print("Table with header, AlteratingRowGrid:")
print(generate_table(rows, columns))


print("Table with header, transposed, AlteratingRowGrid:")
print(generate_table(rows, columns, transpose=True))


print("Table with header, transposed, FancyGrid:")
print(generate_table(rows, columns, grid_style=FancyGrid(), transpose=True))

print("Table with header, transposed, SparseGrid:")
print(generate_table(rows, columns, grid_style=SparseGrid(), transpose=True))


columns2 = (Column('Col1', attrib=KEY3),
            Column('Col2', attrib=KEY2),
            Column('Col3', attrib=KEY1),
            Column('Col4', attrib=KEY4))


print("Table with header, Columns rearranged")
print(generate_table(rows, columns2))
