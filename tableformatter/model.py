# coding=utf-8
import enum

from .colors import TableColors
from .typing_wrapper import Callable, Union


class Options(object):
    COL_OPT_WIDTH = 'col.width'
    COL_OPT_WRAP_MODE = 'col.wrap.mode'
    COL_OPT_WRAP_INDENT_PREFIX = 'col.wrap.indent.prefix'
    COL_OPT_FIELD_FORMATTER = 'col.field.formatter'
    COL_OPT_OBJECT_FORMATTER = 'col.object.formatter'
    COL_OPT_HEADER_HALIGN = 'col.header.align.horiz'
    COL_OPT_HEADER_VALIGN = 'col.header.align.vert'
    COL_OPT_CELL_HALIGN = 'col.cell.align.horiz'
    COL_OPT_CELL_VALIGN = 'col.cell.align.vert'
    COL_OPT_CELL_PADDING = 'col.cell.pad.width'
    COL_OPT_ATTRIB_NAME = 'col.attrib.name'

    ROW_OPT_TEXT_COLOR = 'row.color.fore'
    ROW_OPT_TEXT_BACKGROUND = 'row.color.back'

    TABLE_OPT_TRANSPOSE = 'table.transpose'
    TABLE_OPT_ROW_HEADER = 'table.row.header'


class ColumnAlignment(enum.Enum):
    """Column alignment"""
    AlignLeft = 0
    AlignCenter = 1
    AlignRight = 2
    AlignTop = 10
    AlignBottom = 12

    def format_string(self):
        """Return the format string for this alignment"""
        if self == ColumnAlignment.AlignLeft:
            return '<'
        elif self == ColumnAlignment.AlignCenter:
            return '^'
        elif self == ColumnAlignment.AlignRight:
            return '>'
        elif self in (ColumnAlignment.AlignTop, ColumnAlignment.AlignBottom):
            return ''
        else:
            raise Exception('Invalid enumeration value')


class WrapMode(enum.Enum):
    """Cell wrap mode"""
    WRAP = 0
    """Wraps the cell contents"""
    WRAP_WITH_INDENT = 1
    """Wraps the cell contents and indents the wrapped lines with string defined in the column's wrap prefix"""
    TRUNCATE_END = 2
    """Truncates the end of the line with an ellipsis to indicate truncation"""
    TRUNCATE_FRONT = 3
    """Truncates the beginning of the line with an ellipsis to indicate truncation"""
    TRUNCATE_MIDDLE = 4
    """Truncates the middle of the line with an ellipsis to indicate truncation"""
    TRUNCATE_HARD = 5
    """Truncates the end of the line with no truncation indicator"""


def Column(col_name: str,
           width: int = None,
           attrib: str = None,
           wrap_mode: WrapMode = None,
           wrap_prefix: str = None,
           cell_padding: int = None,
           header_halign: ColumnAlignment = None,
           header_valign: ColumnAlignment = None,
           cell_halign: ColumnAlignment = None,
           cell_valign: ColumnAlignment = None,
           formatter: Callable = None,
           obj_formatter: Callable = None):
    """
    Processes column options and generates a tuple in the format the TableFormatter expects

    :param col_name: Column name to display
    :param width: Number of displayed terminal characters. Unicode wide characters count as 2 displayed characters.
    :param attrib: The name of the object attribute to look up for cell contents on this column
    :param wrap_mode: Defines how to handle long cells that must be wrapped or truncated
    :param wrap_prefix: String to display at the beginning of each wrapped line in a cell
    :param cell_padding: Number of padding spaces to the left and right of each cell
    :param header_halign: Horizontal alignment of the column header
    :param header_valign: Vertical alignment of the column header
    :param cell_halign: Horizontal alignment of the cells in this column
    :param cell_valign: Vertical alignment of the cells in this column
    :param formatter: Callable that can process the value in this column for display
    :param obj_formatter: Callable that processes the row object to generate content for this column
    :return: A column tuple the TableFormatter expects
    """
    opts = dict()
    if width is not None:
        opts[Options.COL_OPT_WIDTH] = width
    if attrib is not None:
        opts[Options.COL_OPT_ATTRIB_NAME] = attrib
    if wrap_mode is not None:
        opts[Options.COL_OPT_WRAP_MODE] = wrap_mode
    if wrap_prefix is not None:
        opts[Options.COL_OPT_WRAP_INDENT_PREFIX] = wrap_prefix
    if cell_padding is not None:
        opts[Options.COL_OPT_CELL_PADDING] = cell_padding
    if header_halign is not None:
        opts[Options.COL_OPT_HEADER_HALIGN] = header_halign
    if header_valign is not None:
        opts[Options.COL_OPT_HEADER_VALIGN] = header_valign
    if cell_halign is not None:
        opts[Options.COL_OPT_CELL_HALIGN] = cell_halign
    if cell_valign is not None:
        opts[Options.COL_OPT_CELL_VALIGN] = cell_valign
    if formatter is not None:
        opts[Options.COL_OPT_FIELD_FORMATTER] = formatter
    if obj_formatter is not None:
        opts[Options.COL_OPT_OBJECT_FORMATTER] = obj_formatter
    if len(opts.keys()) == 0:
        return col_name
    else:
        return col_name, opts


def Row(*args, text_color: Union[TableColors, str] = None):
    """
    Processes row options and generates a tuple in the format the TableFormatter expects
    :param args: Can be either 1 object or a list of values
    :param text_color: text color to use when displaying this row
    :return: Tuple formatted for the TableFormatter to consume
    """
    opts = dict()

    if text_color is not None:
        opts[Options.ROW_OPT_TEXT_COLOR] = text_color

    row = list(args)
    if opts:
        row.append(opts)
    return tuple(row)
