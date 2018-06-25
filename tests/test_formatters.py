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
tf.set_default_grid(tf.AlternatingRowGrid('', '', ''))


class MyRowObject(object):
    """Simple object to demonstrate using a list of objects with TableFormatter"""
    def __init__(self, field1: int, field2: int, field3: int, field4: int):
        self.field1 = field1
        self.field2 = field2
        self._field3 = field3
        self.field4 = field4

    def get_field3(self):
        """Demonstrates accessing object functions"""
        return self._field3


def multiply(row_obj: MyRowObject):
    """Demonstrates an object formatter function"""
    return str(row_obj.get_field3() * row_obj.field4)


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


def test_fmt_obj_rows():
    expected = '''
╔═══════════╤═══════════════════╤═════╤═══════╤════════════╗
║           │                   │ Num │       │            ║
║ First     │ Second            │ 1   │ Num 2 │ Multiplied ║
╠═══════════╪═══════════════════╪═════╪═══════╪════════════╣
║           │                   │ 17  │ 4     │ 68         ║
║ 123.00  B │               123 │ 5   │ 56    │ 280        ║
║ 123.00  B │               123 │ 5   │ 56    │ 280        ║
║  12.06 KB │            12,345 │ 23  │ 8     │ 184        ║
║  11.77 MB │        12,345,678 │ 4   │ 9     │ 36         ║
║   1.15 GB │     1,234,567,890 │ 7   │ 5     │ 35         ║
║   1.12 TB │ 1,234,567,890,123 │ 7   │ 5     │ 35         ║
╚═══════════╧═══════════════════╧═════╧═══════╧════════════╝
'''.lstrip('\n')
    rows = [MyRowObject(None, None, 17, 4),
            MyRowObject('123', '123', 5, 56),
            MyRowObject(123, 123, 5, 56),
            MyRowObject(12345, 12345, 23, 8),
            MyRowObject(12345678, 12345678, 4, 9),
            MyRowObject(1234567890, 1234567890, 7, 5),
            MyRowObject(1234567890123, 1234567890123, 7, 5)]

    columns = (tf.Column('First', width=20, attrib='field1', formatter=tf.FormatBytes(),
                         cell_halign=tf.ColumnAlignment.AlignRight),
               tf.Column('Second', attrib='field2', formatter=tf.FormatCommas(),
                         cell_halign=tf.ColumnAlignment.AlignRight),
               tf.Column('Num 1', width=3, attrib='get_field3'),
               tf.Column('Num 2', attrib='field4'),
               tf.Column('Multiplied', obj_formatter=multiply))
    table = tf.generate_table(rows, columns)
    assert table == expected


def test_fmt_tuple_rows():
    expected = '''
╔═══════════╤═══════════════════╤═══════╤═══════════╤════════════╗
║ First     │ Second            │ Num 1 │ Num 2     │ Multiplied ║
╠═══════════╪═══════════════════╪═══════╪═══════════╪════════════╣
║           │                   │ 17    │ Four      │ 68         ║
║ 123.00  B │               123 │ 5     │ Fifty-six │ 280        ║
║ 123.00  B │               123 │ 5     │ Fifty-six │ 280        ║
║  12.06 KB │            12,345 │ 23    │ Eight     │ 184        ║
║  11.77 MB │        12,345,678 │ 4     │ Nine      │ 36         ║
║   1.15 GB │     1,234,567,890 │ 7     │ Five      │ 35         ║
║   1.12 TB │ 1,234,567,890,123 │ 7     │ Five      │ 35         ║
╚═══════════╧═══════════════════╧═══════╧═══════════╧════════════╝
'''.lstrip('\n')

    rows = [(None, None, 17, 4, None),
            ('123', '123', 5, 56, None),
            (123, 123, 5, 56, None),
            (12345, 12345, 23, 8, None),
            (12345678, 12345678, 4, 9, None),
            (1234567890, 1234567890, 7, 5, None),
            (1234567890123, 1234567890123, 7, 5, None)]

    columns = (tf.Column('First', width=20, formatter=tf.FormatBytes(), cell_halign=tf.ColumnAlignment.AlignRight),
               tf.Column('Second', formatter=tf.FormatCommas(), cell_halign=tf.ColumnAlignment.AlignRight),
               tf.Column('Num 1'),
               tf.Column('Num 2', formatter=int2word),
               tf.Column('Multiplied', obj_formatter=multiply_tuple))

    table = tf.generate_table(rows, columns)

    assert table == expected
