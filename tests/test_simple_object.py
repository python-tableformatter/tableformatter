# coding=utf-8
"""
Unit testing of tableformatter with simple cases using a list of objects for the table entries.
"""
import pytest

import tableformatter as tf


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


# Make the test results reproducible regardless of what color libraries are installed
tf.TableColors.set_color_library('none')


@pytest.fixture
def rows():
    r = [MyRowObject('A1', 'A2', 'A3', 'A4'),
         MyRowObject('B1', 'B2\nB2\nB2', 'B3', 'B4'),
         MyRowObject('C1', 'C2', 'C3', 'C4'),
         MyRowObject('D1', 'D2', 'D3', 'D4')]
    return r


@pytest.fixture
def cols():
    columns = (tf.Column('Col1', attrib='field1'),
               tf.Column('Col2', attrib='field2'),
               tf.Column('Col3', attrib='get_field3'),
               tf.Column('Col4', attrib='field4'))
    return columns


def test_object_table_with_header(rows, cols):
    expected = '╔══════╤══════╤══════╤══════╗\n║ Col1 │ Col2 │ Col3 │ Col4 ║\n╠══════╪══════╪══════╪══════╣\n║ A1   │ A2   │ A3   │ A4   ║\n║ B1   │ B2   │ B3   │ B4   ║\n║      │ B2   │      │      ║\n║      │ B2   │      │      ║\n║ C1   │ C2   │ C3   │ C4   ║\n║ D1   │ D2   │ D3   │ D4   ║\n╚══════╧══════╧══════╧══════╝\n'
    table = tf.generate_table(rows, cols)
    assert table == expected
