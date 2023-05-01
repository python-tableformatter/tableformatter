# coding=utf-8
"""
Unit testing of tableformatter with simple cases
- with a list of tuples as table entries
- using a list of objects for the table entries
"""
import pytest

import tableformatter as tablefmt
from collections import namedtuple

# Make the test results reproducible regardless of what color libraries are installed
tablefmt.TableColors.set_color_library('none')
tablefmt.set_default_grid(tablefmt.AlternatingRowGrid('', '', ''))


class MyRowObject(object):
    """Simple object to demonstrate using a list of objects with TableFormatter"""
    def __init__(self, field1: str, field2: str, field3: int, field4: int):
        self.field1 = field1
        self.field2 = field2
        self._field3 = field3
        self.field4 = field4

    def get_field3(self):
        """Demonstrates accessing object functions"""
        return self._field3


NamedTupleRow = namedtuple('NamedTupleRow', 'field1,field2,field3,field4')
"""Example named tuple to demonstrate usage with TableFormatter"""


def multiply(row_obj: MyRowObject):
    """Demonstrates an object formatter function"""
    return str(row_obj.get_field3() * row_obj.field4)


def multiply_named_tuple(row_job):
    return str(row_job.field3 * row_job.field4)


def multiply_tuple(row_obj):
    """Demonstrates an object formatter function"""
    return str(row_obj[2] * row_obj[3])


def int2word(num, separator="-"):
    """Demonstrates a field formatter function
    From: https://codereview.stackexchange.com/questions/156590/create-the-english-word-for-a-number
    """
    ones_and_teens = {0: "Zero", 1: 'One', 2: 'Two', 3: 'Three',
                      4: 'Four', 5: 'Five', 6: 'Six', 7: 'Seven',
                      8: 'Eight', 9: 'Nine', 10: 'Ten', 11: 'Eleven',
                      12: 'Twelve', 13: 'Thirteen', 14: 'Fourteen',
                      15: 'Fifteen', 16: 'Sixteen', 17: 'Seventeen',
                      18: 'Eighteen', 19: 'Nineteen'}
    twenty2ninety = {2: 'Twenty', 3: 'Thirty', 4: 'Forty', 5: 'Fifty',
                     6: 'Sixty', 7: 'Seventy', 8: 'Eighty', 9: 'Ninety', 0: ""}

    if 0 <= num < 19:
        return ones_and_teens[num]
    elif 20 <= num <= 99:
        tens, below_ten = divmod(num, 10)
        if below_ten > 0:
            words = twenty2ninety[tens] + separator + \
                ones_and_teens[below_ten].lower()
        else:
            words = twenty2ninety[tens]
        return words

    elif 100 <= num <= 999:
        hundreds, below_hundred = divmod(num, 100)
        tens, below_ten = divmod(below_hundred, 10)
        if below_hundred == 0:
            words = ones_and_teens[hundreds] + separator + "hundred"
        elif below_ten == 0:
            words = ones_and_teens[hundreds] + separator + \
                "hundred" + separator + twenty2ninety[tens].lower()
        else:
            if tens > 0:
                words = ones_and_teens[hundreds] + separator + "hundred" + separator + twenty2ninety[
                    tens].lower() + separator + ones_and_teens[below_ten].lower()
            else:
                words = ones_and_teens[
                    hundreds] + separator + "hundred" + separator + ones_and_teens[below_ten].lower()
        return words

    else:
        print("num out of range")

# These tests insert an R and G prefix at the beginning of cells that would
# otherwise have a row color defined. This allows us to test the insertion
# of color escape sequences with no color library installed.


def test_obj_rows():
    expected = '''
╔══════════════════════╤════════╤═════╤═══════╤════════════╗
║                      │        │ Num │       │            ║
║ First                │ Second │ 1   │ Num 2 │ Multiplied ║
╠══════════════════════╪════════╪═════╪═══════╪════════════╣
║ RLonger text that     │ RA2     │ R5   │ R56    │ R280        ║
║ Rwill trigger the     │        │     │       │            ║
║ Rcolumn wrapping      │        │     │       │            ║
║ GB1                   │ GB2     │ G23  │ G8     │ G184        ║
║                      │ GB2     │     │       │            ║
║                      │ GB2     │     │       │            ║
║ C1                   │ C2     │ 4   │ 9     │ 36         ║
║ D1                   │ D2     │ 7   │ 5     │ 35         ║
╚══════════════════════╧════════╧═════╧═══════╧════════════╝
'''.lstrip('\n')
    rows = [tablefmt.Row(MyRowObject('Longer text that will trigger the column wrapping', 'A2', 5, 56),
                   text_color='R'),
            tablefmt.Row(MyRowObject('B1', 'B2\nB2\nB2', 23, 8),
                   text_color='G'),
            MyRowObject('C1', 'C2', 4, 9),
            MyRowObject('D1', 'D2', 7, 5)]

    columns = (tablefmt.Column('First', width=20, attrib='field1'),
               tablefmt.Column('Second', attrib='field2'),
               tablefmt.Column('Num 1', width=3, attrib='get_field3'),
               tablefmt.Column('Num 2', attrib='field4'),
               tablefmt.Column('Multiplied', obj_formatter=multiply))
    table = tablefmt.generate_table(rows, columns)
    assert table == expected


def test_namedtuple_rows():
    expected = '''
╔══════════════════════╤════════╤═════╤═══════╤════════════╗
║                      │        │ Num │       │            ║
║ First                │ Second │ 1   │ Num 2 │ Multiplied ║
╠══════════════════════╪════════╪═════╪═══════╪════════════╣
║ RLonger text that     │ RA2     │ R5   │ R56    │ R280        ║
║ Rwill trigger the     │        │     │       │            ║
║ Rcolumn wrapping      │        │     │       │            ║
║ GB1                   │ GB2     │ G23  │ G8     │ G184        ║
║                      │ GB2     │     │       │            ║
║                      │ GB2     │     │       │            ║
║ C1                   │ C2     │ 4   │ 9     │ 36         ║
║ D1                   │ D2     │ 7   │ 5     │ 35         ║
╚══════════════════════╧════════╧═════╧═══════╧════════════╝
'''.lstrip('\n')
    rows = [tablefmt.Row(NamedTupleRow('Longer text that will trigger the column wrapping', 'A2', 5, 56),
                   text_color='R'),
            tablefmt.Row(NamedTupleRow('B1', 'B2\nB2\nB2', 23, 8),
                   text_color='G'),
            NamedTupleRow('C1', 'C2', 4, 9),
            NamedTupleRow('D1', 'D2', 7, 5)]

    columns = (tablefmt.Column('First', width=20, attrib='field1'),
               tablefmt.Column('Second', attrib='field2'),
               tablefmt.Column('Num 1', width=3, attrib='field3'),
               tablefmt.Column('Num 2', attrib='field4'),
               tablefmt.Column('Multiplied', obj_formatter=multiply_named_tuple))
    table = tablefmt.generate_table(rows, columns)
    assert table == expected


def test_tuple_rows():
    expected = '''
╔══════════════════════╤════════╤═══════╤═══════════╤════════════╗
║ First                │ Second │ Num 1 │ Num 2     │ Multiplied ║
╠══════════════════════╪════════╪═══════╪═══════════╪════════════╣
║ RLonger text that wil │ RA2     │ R5     │ RFifty-six │ R280        ║
║ GB1                   │ GB2     │ G23    │ GEight     │ G184        ║
║                      │ GB2     │       │           │            ║
║                      │ GB2     │       │           │            ║
║ C1                   │ C2     │ 4     │ Nine      │ 36         ║
║ D1                   │ D2     │ 7     │ Five      │ 35         ║
╚══════════════════════╧════════╧═══════╧═══════════╧════════════╝
'''.lstrip('\n')

    rows = [tablefmt.Row('Longer text that will trigger the column wrapping', 'A2', 5, 56, None,
                   text_color='R'),
            tablefmt.Row('B1', 'B2\nB2\nB2', 23, 8, None,
                   text_color='G'),
            ('C1', 'C2', 4, 9, None),
            ('D1', 'D2', 7, 5, None)]

    columns = (tablefmt.Column('First', width=20, wrap_mode=tablefmt.WrapMode.TRUNCATE_HARD),
               tablefmt.Column('Second'),
               tablefmt.Column('Num 1'),
               tablefmt.Column('Num 2', formatter=int2word),
               tablefmt.Column('Multiplied', obj_formatter=multiply_tuple))

    table = tablefmt.generate_table(rows, columns)

    assert table == expected
