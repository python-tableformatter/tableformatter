#!/usr/bin/env python
# coding=utf-8
"""
Demonstration of all of the per-Column customizations that are available.
"""
import tableformatter as tf


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


rows = [MyRowObject('Longer text that will trigger the column wrapping', 'A2', 5, 56),
        MyRowObject('B1', 'B2\nB2\nB2', 23, 8),
        MyRowObject('C1', 'C2', 4, 9),
        MyRowObject('D1', 'D2', 7, 5)]


columns = (tf.Column('First', width=20, attrib='field1'),
           tf.Column('Second', attrib='field2'),
           tf.Column('Num 1', width=3, attrib='get_field3'),
           tf.Column('Num 2', attrib='field4'),
           tf.Column('Multiplied', obj_formatter=multiply))
print("First: Wrapped\nMultiplied: object formatter")
print(tf.generate_table(rows, columns))


columns = (tf.Column('First', width=20, attrib='field1', wrap_mode=tf.WrapMode.WRAP_WITH_INDENT),
           tf.Column('Second', attrib='field2'),
           tf.Column('Num 1', width=3, attrib='get_field3', header_halign=tf.ColumnAlignment.AlignCenter),
           tf.Column('Num 2', attrib='field4'),
           tf.Column('Multiplied', attrib=None, obj_formatter=multiply))
print("First: Wrapped with indent\nNum 1: header align center")
print(tf.generate_table(rows, columns))


columns = (tf.Column('First', width=20, attrib='field1', wrap_mode=tf.WrapMode.WRAP_WITH_INDENT,
                     wrap_prefix='>>> '),
           tf.Column('Second', attrib='field2', cell_halign=tf.ColumnAlignment.AlignCenter),
           tf.Column('Num 1', width=3, attrib='get_field3', header_halign=tf.ColumnAlignment.AlignRight),
           tf.Column('Num 2', attrib='field4', header_valign=tf.ColumnAlignment.AlignTop),
           tf.Column('Multiplied', attrib=None, obj_formatter=multiply))
print("First: Wrapped with indent, custom wrap prefix\n"
      "Second: Header align center\n"
      "Num 1: header align right\n"
      "Num 2: header align top")
print(tf.generate_table(rows, columns))


columns = (tf.Column('First', width=20, attrib='field1', wrap_mode=tf.WrapMode.TRUNCATE_END),
           tf.Column('Second', attrib='field2', cell_padding=3),
           tf.Column('Num 1', width=3, attrib='get_field3'),
           tf.Column('Num 2', attrib='field4'),
           tf.Column('Multiplied', attrib=None, obj_formatter=multiply))
print("First: Truncate end\n"
      "Second: cell padding 3 spaces")
print(tf.generate_table(rows, columns))


columns = (tf.Column('First', width=20, attrib='field1', wrap_mode=tf.WrapMode.TRUNCATE_FRONT),
           tf.Column('Second', attrib='field2', cell_padding=5, cell_halign=tf.ColumnAlignment.AlignRight),
           tf.Column('Num 1', attrib='get_field3'),
           tf.Column('Num 2', attrib='field4'),
           tf.Column('Multiplied', attrib=None, obj_formatter=multiply))
print("First; Truncate Front\n"
      "Second: cell align right, cell padding=5")
print(tf.generate_table(rows, columns))


columns = (tf.Column('First', width=20, attrib='field1', wrap_mode=tf.WrapMode.TRUNCATE_MIDDLE),
           tf.Column('Second', attrib='field2'),
           tf.Column('Num 1', attrib='get_field3'),
           tf.Column('Num 2', attrib='field4', cell_valign=tf.ColumnAlignment.AlignBottom),
           tf.Column('Multiplied', attrib=None, obj_formatter=multiply))
print("First: Truncate Middle\nNum 2: cell align bottom")
print(tf.generate_table(rows, columns))


columns = (tf.Column('First', width=20, attrib='field1', wrap_mode=tf.WrapMode.TRUNCATE_HARD),
           tf.Column('Second', attrib='field2'),
           tf.Column('Num 1', attrib='get_field3'),
           tf.Column('Num 2', attrib='field4', formatter=int2word),
           tf.Column('Multiplied', attrib=None, obj_formatter=multiply))
print("First: Truncate Hard\nNum 2: Field formatter")
print(tf.generate_table(rows, columns))
