# coding=utf-8
"""
Unit testing the variety of column customizations available
"""
import pytest

import tableformatter as tablefmt

# Make the test results reproducible regardless of what color libraries are installed
tablefmt.TableColors.set_color_library('none')
tablefmt.set_default_grid(tablefmt.AlternatingRowGrid('', ''))


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


def multiply(row_obj: MyRowObject):
    """Demonstrates an object formatter function"""
    return str(row_obj.get_field3() * row_obj.field4)


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


@pytest.fixture
def obj_rows():
    rows = [MyRowObject('Longer text that will trigger the column wrapping', 'A2', 5, 56),
            MyRowObject('B1', 'B2\nB2\nB2', 23, 8),
            MyRowObject('C1', 'C2', 4, 9),
            MyRowObject('D1', 'D2', 7, 5)]
    return rows


def test_wrapped_object_formatter(obj_rows):
    columns = (tablefmt.Column('First', width=20, attrib='field1'),
               tablefmt.Column('Second', attrib='field2'),
               tablefmt.Column('Num 1', width=3, attrib='get_field3'),
               tablefmt.Column('Num 2', attrib='field4'),
               tablefmt.Column('Multiplied', obj_formatter=multiply))
    table = tablefmt.generate_table(obj_rows, columns)
    expected = '''
╔══════════════════════╤════════╤═════╤═══════╤════════════╗
║                      │        │ Num │       │            ║
║ First                │ Second │ 1   │ Num 2 │ Multiplied ║
╠══════════════════════╪════════╪═════╪═══════╪════════════╣
║ Longer text that     │ A2     │ 5   │ 56    │ 280        ║
║ will trigger the     │        │     │       │            ║
║ column wrapping      │        │     │       │            ║
║ B1                   │ B2     │ 23  │ 8     │ 184        ║
║                      │ B2     │     │       │            ║
║                      │ B2     │     │       │            ║
║ C1                   │ C2     │ 4   │ 9     │ 36         ║
║ D1                   │ D2     │ 7   │ 5     │ 35         ║
╚══════════════════════╧════════╧═════╧═══════╧════════════╝
'''.lstrip('\n')
    assert table == expected


def test_wrapped_indent_center_header(obj_rows):
    columns = (tablefmt.Column('First', width=20, attrib='field1', wrap_mode=tablefmt.WrapMode.WRAP_WITH_INDENT),
               tablefmt.Column('Second', attrib='field2'),
               tablefmt.Column('Num 1', width=3, attrib='get_field3', header_halign=tablefmt.ColumnAlignment.AlignCenter),
               tablefmt.Column('Num 2', attrib='field4'),
               tablefmt.Column('Multiplied', attrib=None, obj_formatter=multiply))
    table = tablefmt.generate_table(obj_rows, columns)
    expected = '''
╔══════════════════════╤════════╤═════╤═══════╤════════════╗
║                      │        │ Num │       │            ║
║ First                │ Second │  1  │ Num 2 │ Multiplied ║
╠══════════════════════╪════════╪═════╪═══════╪════════════╣
║ Longer text that     │ A2     │ 5   │ 56    │ 280        ║
║  » will trigger the  │        │     │       │            ║
║  » column wrapping   │        │     │       │            ║
║ B1                   │ B2     │ 23  │ 8     │ 184        ║
║                      │ B2     │     │       │            ║
║                      │ B2     │     │       │            ║
║ C1                   │ C2     │ 4   │ 9     │ 36         ║
║ D1                   │ D2     │ 7   │ 5     │ 35         ║
╚══════════════════════╧════════╧═════╧═══════╧════════════╝
'''.lstrip('\n')
    assert table == expected


def test_wrapped_custom_indent_header_right_header_top(obj_rows):
    columns = (tablefmt.Column('First', width=20, attrib='field1', wrap_mode=tablefmt.WrapMode.WRAP_WITH_INDENT,
                         wrap_prefix='>>> '),
               tablefmt.Column('Second', attrib='field2', cell_halign=tablefmt.ColumnAlignment.AlignCenter),
               tablefmt.Column('Num 1', width=3, attrib='get_field3', header_halign=tablefmt.ColumnAlignment.AlignRight),
               tablefmt.Column('Num 2', attrib='field4', header_valign=tablefmt.ColumnAlignment.AlignTop),
               tablefmt.Column('Multiplied', attrib=None, obj_formatter=multiply))
    table = tablefmt.generate_table(obj_rows, columns)
    expected = '''
╔══════════════════════╤════════╤═════╤═══════╤════════════╗
║                      │        │ Num │ Num 2 │            ║
║ First                │ Second │   1 │       │ Multiplied ║
╠══════════════════════╪════════╪═════╪═══════╪════════════╣
║ Longer text that     │   A2   │ 5   │ 56    │ 280        ║
║ >>> will trigger the │        │     │       │            ║
║ >>> column wrapping  │        │     │       │            ║
║ B1                   │   B2   │ 23  │ 8     │ 184        ║
║                      │   B2   │     │       │            ║
║                      │   B2   │     │       │            ║
║ C1                   │   C2   │ 4   │ 9     │ 36         ║
║ D1                   │   D2   │ 7   │ 5     │ 35         ║
╚══════════════════════╧════════╧═════╧═══════╧════════════╝
'''.lstrip('\n')
    assert table == expected


def test_truncate_end_custom_padding(obj_rows):
    columns = (tablefmt.Column('First', width=20, attrib='field1', wrap_mode=tablefmt.WrapMode.TRUNCATE_END),
               tablefmt.Column('Second', attrib='field2', cell_padding=3),
               tablefmt.Column('Num 1', width=3, attrib='get_field3'),
               tablefmt.Column('Num 2', attrib='field4'),
               tablefmt.Column('Multiplied', attrib=None, obj_formatter=multiply))
    table = tablefmt.generate_table(obj_rows, columns)
    expected = '''
╔══════════════════════╤════════════╤═════╤═══════╤════════════╗
║                      │            │ Num │       │            ║
║ First                │   Second   │ 1   │ Num 2 │ Multiplied ║
╠══════════════════════╪════════════╪═════╪═══════╪════════════╣
║ Longer text that wi… │   A2       │ 5   │ 56    │ 280        ║
║ B1                   │   B2       │ 23  │ 8     │ 184        ║
║                      │   B2       │     │       │            ║
║                      │   B2       │     │       │            ║
║ C1                   │   C2       │ 4   │ 9     │ 36         ║
║ D1                   │   D2       │ 7   │ 5     │ 35         ║
╚══════════════════════╧════════════╧═════╧═══════╧════════════╝
'''.lstrip('\n')
    assert table == expected


def test_truncate_front_custom_padding_cell_align_right(obj_rows):
    columns = (tablefmt.Column('First', width=20, attrib='field1', wrap_mode=tablefmt.WrapMode.TRUNCATE_FRONT),
               tablefmt.Column('Second', attrib='field2', cell_padding=5, cell_halign=tablefmt.ColumnAlignment.AlignRight),
               tablefmt.Column('Num 1', attrib='get_field3'),
               tablefmt.Column('Num 2', attrib='field4'),
               tablefmt.Column('Multiplied', attrib=None, obj_formatter=multiply))
    table = tablefmt.generate_table(obj_rows, columns)
    expected = '''
╔══════════════════════╤════════════════╤═══════╤═══════╤════════════╗
║ First                │     Second     │ Num 1 │ Num 2 │ Multiplied ║
╠══════════════════════╪════════════════╪═══════╪═══════╪════════════╣
║ …the column wrapping │         A2     │ 5     │ 56    │ 280        ║
║ B1                   │         B2     │ 23    │ 8     │ 184        ║
║                      │         B2     │       │       │            ║
║                      │         B2     │       │       │            ║
║ C1                   │         C2     │ 4     │ 9     │ 36         ║
║ D1                   │         D2     │ 7     │ 5     │ 35         ║
╚══════════════════════╧════════════════╧═══════╧═══════╧════════════╝
'''.lstrip('\n')
    assert table == expected


def test_truncate_middle_cell_align_bottom(obj_rows):
    columns = (tablefmt.Column('First', width=20, attrib='field1', wrap_mode=tablefmt.WrapMode.TRUNCATE_MIDDLE),
               tablefmt.Column('Second', attrib='field2'),
               tablefmt.Column('Num 1', attrib='get_field3'),
               tablefmt.Column('Num 2', attrib='field4', cell_valign=tablefmt.ColumnAlignment.AlignBottom),
               tablefmt.Column('Multiplied', attrib=None, obj_formatter=multiply))
    table = tablefmt.generate_table(obj_rows, columns)
    expected = '''
╔══════════════════════╤════════╤═══════╤═══════╤════════════╗
║ First                │ Second │ Num 1 │ Num 2 │ Multiplied ║
╠══════════════════════╪════════╪═══════╪═══════╪════════════╣
║ Longer t … wrapping  │ A2     │ 5     │ 56    │ 280        ║
║ B1                   │ B2     │ 23    │       │ 184        ║
║                      │ B2     │       │       │            ║
║                      │ B2     │       │ 8     │            ║
║ C1                   │ C2     │ 4     │ 9     │ 36         ║
║ D1                   │ D2     │ 7     │ 5     │ 35         ║
╚══════════════════════╧════════╧═══════╧═══════╧════════════╝
'''.lstrip('\n')
    assert table == expected


def test_truncate_hard_field_formatter(obj_rows):
    columns = (tablefmt.Column('First', width=20, attrib='field1', wrap_mode=tablefmt.WrapMode.TRUNCATE_HARD),
               tablefmt.Column('Second', attrib='field2'),
               tablefmt.Column('Num 1', attrib='get_field3'),
               tablefmt.Column('Num 2', attrib='field4', formatter=int2word),
               tablefmt.Column('Multiplied', attrib=None, obj_formatter=multiply))
    table = tablefmt.generate_table(obj_rows, columns)
    expected = '''
╔══════════════════════╤════════╤═══════╤═══════════╤════════════╗
║ First                │ Second │ Num 1 │ Num 2     │ Multiplied ║
╠══════════════════════╪════════╪═══════╪═══════════╪════════════╣
║ Longer text that wil │ A2     │ 5     │ Fifty-six │ 280        ║
║ B1                   │ B2     │ 23    │ Eight     │ 184        ║
║                      │ B2     │       │           │            ║
║                      │ B2     │       │           │            ║
║ C1                   │ C2     │ 4     │ Nine      │ 36         ║
║ D1                   │ D2     │ 7     │ Five      │ 35         ║
╚══════════════════════╧════════╧═══════╧═══════════╧════════════╝
'''.lstrip('\n')
    assert table == expected

