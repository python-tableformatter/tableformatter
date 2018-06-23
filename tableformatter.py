# coding=utf-8
"""
Formats data into a table
"""
import enum
import re
import textwrap as textw
from typing import List, Iterable, Tuple, Union

from wcwidth import wcswidth

# This whole try/except exists to make sure a Collection type exists for use with optional type hinting and isinstance
try:
    # Python 3.6+ should have Collection in the typing module
    from typing import Collection
except ImportError:
    from typing import Container, Generic, Sized, TypeVar
    # Python 3.5
    # noinspection PyAbstractClass
    class Collection(Generic[TypeVar('T_co', covariant=True)], Container, Sized, Iterable):
        """hack to enable Collection typing"""
        __slots__ = ()

        # noinspection PyPep8Naming
        @classmethod
        def __subclasshook__(cls, C):
            if cls is Collection:
                if any("__len__" in B.__dict__ for B in C.__mro__) and \
                        any("__iter__" in B.__dict__ for B in C.__mro__) and \
                        any("__contains__" in B.__dict__ for B in C.__mro__):
                    return True
            return NotImplemented


ANSI_ESCAPE_RE = re.compile(r'\x1b[^m]*m')
TAB_WIDTH = 4


def _text_wrap(text, width=70):
    """Wrap a single paragraph of text, returning a list of wrapped lines.

    Reformat the single paragraph in 'text' so it fits in lines of no
    more than 'width' columns, and return a list of wrapped lines.  By
    default, tabs in 'text' are expanded with string.expandtabs(), and
    all other whitespace characters (including newline) are converted to
    space.  See TextWrapper class for available keyword args to customize
    wrapping behaviour.
    """
    w = _TableTextWrapper(width=width)
    return w.wrap(text)


def _wcswidth(text):
    """Wraps wcswidth() with stripping of escape characters"""
    stripped = ANSI_ESCAPE_RE.sub('', text)
    return wcswidth(stripped)


# noinspection PyProtectedMember
class _TableTextWrapper(textw.TextWrapper):
    """Internal textwrapper with customized behavior"""
    _whitespace = textw._whitespace + '\\/'

    word_punct = r'[\w!"\'&.,?]'
    letter = r'[^\d\W]'
    whitespace = r'[%s]' % re.escape(_whitespace)
    nowhitespace = '[^' + whitespace[1:]
    wordsep_re = re.compile(r'''
        ( # any whitespace
          %(ws)s+
        | # em-dash between words
          (?<=%(wp)s) -{2,} (?=\w)
        | # word, possibly hyphenated
          %(nws)s+? (?:
            # hyphenated word
              -(?: (?<=%(lt)s{2}-) | (?<=%(lt)s-%(lt)s-))
              (?= %(lt)s -? %(lt)s)
            | # end of word
              (?=%(ws)s|\Z)
            | # em-dash
              (?<=%(wp)s) (?=-{2,}\w)
            )
        )''' % {'wp': word_punct, 'lt': letter,
                'ws': whitespace, 'nws': nowhitespace},
        re.VERBOSE)
    del word_punct, letter, nowhitespace

    # This less funky little regex just split on recognized spaces. E.g.
    #   "Hello there -- you goof-ball, use the -b option!"
    # splits into
    #   Hello/ /there/ /--/ /you/ /goof-ball,/ /use/ /the/ /-b/ /option!/
    wordsep_simple_re = re.compile(r'(%s+)' % whitespace)
    del whitespace

    def __init__(self, width: int = 70, initial_indent: str = '', subsequent_indent: str = ''):
        super().__init__(tabsize=TAB_WIDTH,
                         width=width,
                         initial_indent=initial_indent,
                         subsequent_indent=subsequent_indent)

    def _split(self, text):
        """_split(text : string) -> [string]

        Split the text to wrap into indivisible chunks.  Chunks are
        not quite the same as words; see _wrap_chunks() for full
        details.  As an example, the text
          Look, goof-ball -- use the -b option!
        breaks into the following chunks:
          'Look,', ' ', 'goof-', 'ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', 'option!'
        if break_on_hyphens is True, or in:
          'Look,', ' ', 'goof-ball', ' ', '--', ' ',
          'use', ' ', 'the', ' ', '-b', ' ', option!'
        otherwise.
        """
        if self.break_on_hyphens is True:
            chunks = self.wordsep_re.split(text)
        else:
            chunks = self.wordsep_simple_re.split(text)
        chunks = [c for c in chunks if c]
        return chunks

    def _wrap_chunks(self, chunks):
        """_wrap_chunks(chunks : [string]) -> [string]

        Wrap a sequence of text chunks and return a list of lines of
        length 'self.width' or less.  (If 'break_long_words' is false,
        some lines may be longer than this.)  Chunks correspond roughly
        to words and the whitespace between them: each chunk is
        indivisible (modulo 'break_long_words'), but a line break can
        come between any two chunks.  Chunks should not have internal
        whitespace; ie. a chunk is either all whitespace or a "word".
        Whitespace chunks will be removed from the beginning and end of
        lines, but apart from that whitespace is preserved.
        """
        lines = []
        if self.width <= 0:
            raise ValueError("invalid width %r (must be > 0)" % self.width)
        if self.max_lines is not None:
            if self.max_lines > 1:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent
            if _wcswidth(indent) + _wcswidth(self.placeholder.lstrip()) > self.width:
                raise ValueError("placeholder too large for max width")

        # Arrange in reverse order so items can be efficiently popped
        # from a stack of chucks.
        chunks.reverse()

        while chunks:

            # Start the list of chunks that will make up the current line.
            # cur_len is just the length of all the chunks in cur_line.
            cur_line = []
            cur_len = 0

            # Figure out which static string will prefix this line.
            if lines:
                indent = self.subsequent_indent
            else:
                indent = self.initial_indent

            # Maximum width for this line.
            width = self.width - _wcswidth(indent)

            # First chunk on line is whitespace -- drop it, unless this
            # is the very beginning of the text (ie. no lines started yet).
            if self.drop_whitespace and chunks[-1].strip() == '' and lines:
                del chunks[-1]

            while chunks:
                l = _wcswidth(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + l <= width:
                    cur_line.append(chunks.pop())
                    cur_len += l

                # Nope, this line is full.
                else:
                    break

            # The current line is full, and the next chunk is too big to
            # fit on *any* line (not just this one).
            if chunks and _wcswidth(chunks[-1]) > width:
                self._handle_long_word(chunks, cur_line, cur_len, width)
                cur_len = sum(map(len, cur_line))

            # If the last chunk on this line is all whitespace, drop it.
            if self.drop_whitespace and cur_line and cur_line[-1].strip() == '':
                cur_len -= _wcswidth(cur_line[-1])
                del cur_line[-1]

            if cur_line:
                if (self.max_lines is None or
                    len(lines) + 1 < self.max_lines or
                    (not chunks or
                     self.drop_whitespace and
                     len(chunks) == 1 and
                     not chunks[0].strip()) and cur_len <= width):
                    # Convert current line back to a string and store it in
                    # list of all lines (return value).
                    lines.append(indent + ''.join(cur_line))
                else:
                    while cur_line:
                        if (cur_line[-1].strip() and
                                cur_len + _wcswidth(self.placeholder) <= width):
                            cur_line.append(self.placeholder)
                            lines.append(indent + ''.join(cur_line))
                            break
                        cur_len -= _wcswidth(cur_line[-1])
                        del cur_line[-1]
                    else:
                        if lines:
                            prev_line = lines[-1].rstrip()
                            if (_wcswidth(prev_line) + _wcswidth(self.placeholder) <=
                                    self.width):
                                lines[-1] = prev_line + self.placeholder
                                break
                        lines.append(indent + self.placeholder.lstrip())
                    break

        return lines


def _translate_tabs(text):
    """Translate tab characters into spaces for measurement"""
    tabpos = text.find('\t')
    while tabpos >= 0:
        before_text = text[:tabpos]
        after_text = text[tabpos+1:]
        before_width = _wcswidth(before_text)
        tab_pad = TAB_WIDTH - (before_width % TAB_WIDTH)
        text = before_text + '{: <{width}}'.format('', width=tab_pad) + after_text

        tabpos = text.find('\t')
    return text


def _printable_width(text):
    """Returns the printable width of a string accounting for escape characters and wide-display unicode characters"""
    return _wcswidth(_translate_tabs(text))


# noinspection PyUnresolvedReferences
class TableColors(object):
    """Colors"""
    try:
        from colored import fg, bg, attr

        TEXT_COLOR_WHITE = fg('white')
        TEXT_COLOR_YELLOW = fg(226)
        TEXT_COLOR_RED = fg(196)
        TEXT_COLOR_GREEN = fg(119)
        TEXT_COLOR_BLUE = fg(27)
        BG_COLOR_ROW = bg(234)
        BG_RESET = bg(0)
        BOLD = attr('bold')
        RESET = attr('reset')
    except ImportError:
        try:
            from colorama import Fore, Back, Style

            TEXT_COLOR_WHITE = Fore.WHITE
            TEXT_COLOR_YELLOW = Fore.LIGHTYELLOW_EX
            TEXT_COLOR_RED = Fore.LIGHTRED_EX
            TEXT_COLOR_GREEN = Fore.LIGHTGREEN_EX
            TEXT_COLOR_BLUE = Fore.LIGHTBLUE_EX
            BG_COLOR_ROW = Back.LIGHTBLACK_EX
            BG_RESET = Back.RESET
            BOLD = Style.BRIGHT
            RESET = Fore.RESET + Back.RESET
        except ImportError:
            TEXT_COLOR_WHITE = ''
            TEXT_COLOR_YELLOW = ''
            TEXT_COLOR_RED = ''
            TEXT_COLOR_GREEN = ''
            TEXT_COLOR_BLUE = ''
            BG_COLOR_ROW = ''
            BG_RESET = ''
            BOLD = ''
            RESET = ''

    @classmethod
    def set_color_library(cls, library_name: str) -> None:
        """Manually override the color library being used."""
        if library_name == 'colored':
            from colored import fg, bg, attr

            cls.TEXT_COLOR_WHITE = fg('white')
            cls.TEXT_COLOR_YELLOW = fg(226)
            cls.TEXT_COLOR_RED = fg(196)
            cls.TEXT_COLOR_GREEN = fg(119)
            cls.TEXT_COLOR_BLUE = fg(27)
            cls.BG_COLOR_ROW = bg(234)
            cls.BG_RESET = bg(0)
            cls.BOLD = attr('bold')
            cls.RESET = attr('reset')
        elif library_name == 'colorama':
            from colorama import Fore, Back, Style

            cls.TEXT_COLOR_WHITE = Fore.WHITE
            cls.TEXT_COLOR_YELLOW = Fore.LIGHTYELLOW_EX
            cls.TEXT_COLOR_RED = Fore.LIGHTRED_EX
            cls.TEXT_COLOR_GREEN = Fore.LIGHTGREEN_EX
            cls.TEXT_COLOR_BLUE = Fore.LIGHTBLUE_EX
            cls.BG_COLOR_ROW = Back.LIGHTBLACK_EX
            cls.BG_RESET = Back.RESET
            cls.BOLD = Style.BRIGHT
            cls.RESET = Fore.RESET + Back.RESET
        else:
            cls.TEXT_COLOR_WHITE = ''
            cls.TEXT_COLOR_YELLOW = ''
            cls.TEXT_COLOR_RED = ''
            cls.TEXT_COLOR_GREEN = ''
            cls.TEXT_COLOR_BLUE = ''
            cls.BG_COLOR_ROW = ''
            cls.BG_RESET = ''
            cls.BOLD = ''
            cls.RESET = ''


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


def _pad_columns(text: str, pad_char: str, align: Union[ColumnAlignment, str], width: int):
    """Returns a string padded out to the specified width"""
    text = _translate_tabs(text)
    display_width = _printable_width(text)
    if display_width >= width:
        return text

    if align in (ColumnAlignment.AlignLeft, ColumnAlignment.AlignLeft.format_string()):
        out_text = text
        out_text += '{:{pad}<{width}}'.format('', pad=pad_char, width=width-display_width)
    elif align in (ColumnAlignment.AlignRight, ColumnAlignment.AlignRight.format_string()):
        out_text = '{:{pad}<{width}}'.format('', pad=pad_char, width=width-display_width)
        out_text += text
    elif align in (ColumnAlignment.AlignCenter, ColumnAlignment.AlignCenter.format_string()):
        lead_pad = int((width - display_width) / 2)
        tail_pad = width - display_width - lead_pad

        out_text = '{:{pad}<{width}}'.format('', pad=pad_char, width=lead_pad)
        out_text += text
        out_text += '{:{pad}<{width}}'.format('', pad=pad_char, width=tail_pad)
    else:
        out_text = text
        out_text += '{:{pad}<{width}}'.format('', pad=pad_char, width=width-display_width)

    return out_text


class WrapMode(enum.Enum):
    """Cell wrap mode"""
    WRAP = 0
    WRAP_WITH_INDENT = 1
    TRUNCATE_END = 2
    TRUNCATE_FRONT = 3
    TRUNCATE_MIDDLE = 4
    TRUNCATE_HARD = 5


class FancyGrid(object):
    """Fancy table with grid lines dividing rows and columns"""
    can_wrap = True

    show_header = True

    border_top = True
    border_top_left = '╔'
    border_top_span = '═'
    border_top_right = '╗'
    border_top_col_divider = '╤'
    border_top_header_col_divider = '╦'

    border_header_divider = True
    border_left_header_divider = '╠'
    border_right_header_divider = '╣'
    border_header_divider_span = '═'
    border_header_col_divider = '╪'
    border_header_header_col_divider = '╬'

    border_left = True

    @staticmethod
    def border_left_span(row_index: Union[int, None]):
        return '║'
    border_left_row_divider = '╟'

    border_right = True

    @staticmethod
    def border_right_span(row_index: Union[int, None]):
        return '║'
    border_right_row_divider = '╢'

    col_divider = True

    @staticmethod
    def col_divider_span(row_index: Union[int, None]):
        return '│'

    @staticmethod
    def header_col_divider_span(row_index: Union[int, None]):
        return '║'

    row_divider = True
    row_divider_span = '─'

    row_divider_col_divider = '┼'
    row_divider_header_col_divider = '╫'

    border_bottom = True
    border_bottom_left = '╚'
    border_bottom_right = '╝'
    border_bottom_span = '═'
    border_bottom_col_divider = '╧'
    border_bottom_header_col_divider = '╩'

    cell_pad_char = ' '

    @staticmethod
    def cell_format(text):
        return text


class AlternatingRowGrid(object):
    """Generates alternating black/gray background colors for rows to conserve vertical space"""
    can_wrap = True
    show_header = True

    border_top = True
    border_top_left = '╔'
    border_top_span = '═'
    border_top_right = '╗'
    border_top_col_divider = '╤'
    border_top_header_col_divider = '╦'

    border_header_divider = True
    border_left_header_divider = '╠'
    border_right_header_divider = '╣'
    border_header_divider_span = '═'
    border_header_col_divider = '╪'
    border_header_header_col_divider = '╬'

    border_left = True

    @staticmethod
    def border_left_span(row_index: Union[int, None]):
        if isinstance(row_index, int):
            if row_index % 2 == 0:
                return '║'
            else:
                return TableColors.BG_RESET + '║' + TableColors.BG_COLOR_ROW
        return '║'

    border_left_row_divider = '╟'

    border_right = True

    @staticmethod
    def border_right_span(row_index: Union[int, None]):
        if isinstance(row_index, int):
            if row_index % 2 == 0:
                return '║'
            else:
                return TableColors.BG_RESET + '║'
        return '║'

    border_right_row_divider = '╢'

    col_divider = True

    @staticmethod
    def col_divider_span(row_index : Union[int, None]):
        if isinstance(row_index, int):
            if row_index % 2 == 0:
                return '│'
            else:
                return TableColors.BG_RESET + TableColors.BG_COLOR_ROW + '│'
        return '│'

    @staticmethod
    def header_col_divider_span(row_index: Union[int, None]):
        if isinstance(row_index, int):
            if row_index % 2 == 0:
                return '║'
            else:
                return TableColors.BG_RESET + TableColors.BG_COLOR_ROW + '║'
        return '║'

    row_divider = False
    row_divider_span = ''

    row_divider_col_divider = ''
    row_divider_header_col_divider = ''

    border_bottom = True
    border_bottom_left = '╚'
    border_bottom_right = '╝'
    border_bottom_span = '═'
    border_bottom_col_divider = '╧'
    border_bottom_header_col_divider = '╩'

    cell_pad_char = ' '
    @staticmethod
    def cell_format(text):
        return text


class SparseGrid(object):
    """Sparse grid with no lines at all and no alternating background colors"""
    can_wrap = True
    show_header = False

    border_top = False
    border_top_left = ''
    border_top_span = ''
    border_top_right = ''
    border_top_col_divider = ''
    border_top_header_col_divider = ''

    border_header_divider = False
    border_left_header_divider = ''
    border_right_header_divider = ''
    border_header_divider_span = ''
    border_header_col_divider = ''
    border_header_header_col_divider = ''

    border_left = False

    @staticmethod
    def border_left_span(row_index: Union[int, None]):
        return ''

    border_left_row_divider = ''

    border_right = False

    @staticmethod
    def border_right_span(row_index: Union[int, None]):
        return ''

    border_right_row_divider = ''

    col_divider = True

    @staticmethod
    def col_divider_span(row_index: Union[int, None]):
        return ''

    @staticmethod
    def header_col_divider_span(row_index: Union[int, None]):
        return ''

    row_divider = False
    row_divider_span = ''

    row_divider_col_divider = ''
    row_divider_header_col_divider = ''

    border_bottom = True
    border_bottom_left = ''
    border_bottom_right = ''
    border_bottom_span = ''
    border_bottom_col_divider = ''
    border_bottom_header_col_divider = ''

    cell_pad_char = ' '

    @staticmethod
    def cell_format(text):
        return text


def generate_table(rows, columns: Collection[Union[str, Tuple[str, dict]]]=None, grid_style=AlternatingRowGrid, transpose=False):
    """Convenience  function to easily generate a table from rows/columns"""
    show_headers = True
    use_attrib = False
    if isinstance(columns, Collection) and len(columns) > 0:
        columns = list(columns)

        attrib_count = 0
        for column in columns:
            if isinstance(column, tuple) and len(column) > 1 and isinstance(column[1], dict):
                if TableFormatter.COL_OPT_ATTRIB_NAME in column[1].keys():
                    attrib = column[1][TableFormatter.COL_OPT_ATTRIB_NAME]
                    if isinstance(attrib, str) and len(attrib) > 0:
                        attrib_count += 1
        if attrib_count == len(columns):
            use_attrib = True

    if not columns:
        show_headers = False
        max_count = 0
        for row in rows:
            if len(row) > max_count:
                max_count = len(row)
        columns = [str(i) for i in range(0, max_count)]
    formatter = TableFormatter(columns, grid_style=grid_style, show_header=show_headers,
                               use_attribs=use_attrib, transpose=transpose)
    return formatter.generate_table(rows)


def Column(col_name,
           width=None,
           attrib=None,
           wrap_mode=None,
           header_halign=None,
           header_valign=None,
           cell_halign=None,
           cell_valign=None,
           formatter=None,
           obj_formatter=None):
    """Convenience function to simplify column definition"""
    opts = dict()
    if width is not None:
        opts[TableFormatter.COL_OPT_WIDTH] = width
    if attrib is not None:
        opts[TableFormatter.COL_OPT_ATTRIB_NAME] = attrib
    if wrap_mode is not None:
        opts[TableFormatter.COL_OPT_WRAP_MODE] = wrap_mode
    if header_halign is not None:
        opts[TableFormatter.COL_OPT_HEADER_HALIGN] = header_halign
    if header_valign is not None:
        opts[TableFormatter.COL_OPT_HEADER_VALIGN] = header_valign
    if cell_halign is not None:
        opts[TableFormatter.COL_OPT_CELL_HALIGN] = cell_halign
    if cell_valign is not None:
        opts[TableFormatter.COL_OPT_CELL_VALIGN] = cell_valign
    if formatter is not None:
        opts[TableFormatter.COL_OPT_FIELD_FORMATTER] = formatter
    if obj_formatter is not None:
        opts[TableFormatter.COL_OPT_OBJECT_FORMATTER] = obj_formatter
    if len(opts.keys()) == 0:
        return col_name
    else:
        return col_name, opts


class TableFormatter(object):
    """
    Simple implementation of an ascii table formatter.
    Allows definition of max column width
    Allows definition of custom cell format functions
    """
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

    def __init__(self,
                 columns: Collection[Union[str, Tuple[str, dict]]],
                 cell_padding: int = 1,
                 max_column_width: int = 0,
                 default_header_horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                 default_header_vert_align: ColumnAlignment = ColumnAlignment.AlignBottom,
                 default_cell_horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                 default_cell_vert_align: ColumnAlignment = ColumnAlignment.AlignTop,
                 grid_style=AlternatingRowGrid,
                 show_header=True,
                 use_attribs=False,
                 transpose=False,
                 row_show_header=False):
        """
        :param columns: list of tuples: (column name, [max width])
        :param cell_padding: number of spaces to pad to the left/right of each column
        """
        self._columns = columns
        self._grid_style = grid_style
        self._column_names = []
        self._column_attribs = [None for i in range(len(columns))]
        self._column_opts = {}
        self._global_opts = {TableFormatter.COL_OPT_HEADER_HALIGN: default_header_horiz_align,
                             TableFormatter.COL_OPT_HEADER_VALIGN: default_header_vert_align,
                             TableFormatter.COL_OPT_CELL_HALIGN: default_cell_horiz_align,
                             TableFormatter.COL_OPT_CELL_VALIGN: default_cell_vert_align,
                             TableFormatter.COL_OPT_WIDTH: max_column_width,
                             TableFormatter.COL_OPT_CELL_PADDING: cell_padding,
                             TableFormatter.COL_OPT_WRAP_MODE: WrapMode.WRAP,
                             TableFormatter.COL_OPT_WRAP_INDENT_PREFIX: ' » ',
                             TableFormatter.COL_OPT_ATTRIB_NAME: use_attribs,
                             TableFormatter.TABLE_OPT_TRANSPOSE: transpose,
                             TableFormatter.TABLE_OPT_ROW_HEADER: row_show_header}
        self._show_header = show_header

        for col_index, column in enumerate(columns):
            if isinstance(column, tuple) and len(column) > 1 and isinstance(column[1], dict):
                self._column_names.append(column[0])
                self._column_opts[col_index] = column[1]

                if use_attribs and TableFormatter.COL_OPT_ATTRIB_NAME in self._column_opts[col_index].keys():
                    self._column_attribs[col_index] = self._column_opts[col_index][TableFormatter.COL_OPT_ATTRIB_NAME]

            elif isinstance(column, str):
                self._column_names.append(column)
            else:
                self._column_names.append(str(column))

        if use_attribs:
            for col_index, attrib in enumerate(self._column_attribs):
                if attrib is None:
                    raise ValueError('Attribute name is required for {}'.format(self._column_names[col_index]))

    def set_default_header_alignment(self,
                                     horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                                     vert_align: ColumnAlignment = ColumnAlignment.AlignBottom):
        """
        Set the default header alignment for all columns
        :param horiz_align:
        :param vert_align:
        """
        self._global_opts[TableFormatter.COL_OPT_HEADER_HALIGN] = horiz_align
        self._global_opts[TableFormatter.COL_OPT_HEADER_VALIGN] = vert_align

    def set_default_cell_alignment(self,
                                   horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                                   vert_align: ColumnAlignment = ColumnAlignment.AlignTop):
        """
        Set the default cell alignment for all columns
        :param horiz_align:
        :param vert_align
        """
        self._global_opts[TableFormatter.COL_OPT_CELL_HALIGN] = horiz_align
        self._global_opts[TableFormatter.COL_OPT_CELL_VALIGN] = vert_align

    def set_formatter(self, column: Union[int, str], format_function):
        """
        Optionally specify a custom format function for a column index
        :param column: column position this applies to
        :param format_function: function to call to format the value. Signature: def myfunction(field_value):
        """
        self._set_column_option(column, TableFormatter.COL_OPT_FIELD_FORMATTER,  format_function)

    def set_header_alignment(self,
                             column: Union[int, str],
                             horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                             vert_align: ColumnAlignment = ColumnAlignment.AlignBottom):
        """
        Specify the header alignment for a specific column
        :param column:
        :param horiz_align: horizontal alignment
        :param vert_align: vertical alignment
        """
        self._set_column_option(column, TableFormatter.COL_OPT_HEADER_HALIGN, horiz_align)
        self._set_column_option(column, TableFormatter.COL_OPT_HEADER_VALIGN, vert_align)

    def set_cell_alignment(self,
                           column: Union[int, str],
                           horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                           vert_align: ColumnAlignment = ColumnAlignment.AlignTop):
        """
        Specify the cell alignment for a specific column
        :param column:
        :param horiz_align:
        :param vert_align:
        """
        self._set_column_option(column, TableFormatter.COL_OPT_CELL_HALIGN, horiz_align)
        self._set_column_option(column, TableFormatter.COL_OPT_CELL_VALIGN, vert_align)

    def generate_table(self, entries: List[Iterable], force_transpose=False):
        """
        Generate the table from a list of entries

        Optionally, add a dict() to the end of the entries tuple containing
        option specifiers to customize behavior.
        Currently only 1 specifier is available: OPT_TEXT_COLOR

        :param entries:
        :return: table formatted string
        """
        col_headings = []    # heading string for each column
        col_widths = [0 for _ in range(len(self._columns))]      # width of each column
        col_max_widths = [0 for _ in range(len(self._columns))]  # maximum width for each column
        rows = []            # list of row entries.
                             # Each row is a list of cell entries.
                             # Each cell is a list of line entries.
                             # Each line entry is a string
        row_opts = []
        halign_headers = []   # Alignment for header by column
        halign_cells = []     # Alignment for cell by column
        valign_headers = []
        valign_cells = []
        use_attribs = self._global_opts[TableFormatter.COL_OPT_ATTRIB_NAME]
        transpose = self._global_opts[TableFormatter.TABLE_OPT_TRANSPOSE] or force_transpose
        show_header = self._show_header and (self._grid_style.show_header or transpose)
        show_row_header = self._global_opts[TableFormatter.TABLE_OPT_ROW_HEADER]

        # combine formatter defaults and specifiers
        for column_index, column in enumerate(self._columns):
            # identify the max width for the column

            max_width = self._get_column_option(column_index, TableFormatter.COL_OPT_WIDTH)
            col_max_widths[column_index] = max_width

            if show_header:
                col_heading = self._column_names[column_index]
                col_headings.append([col_heading])
                col_widths[column_index] = _printable_width(col_heading)

                halign_headers.append(self._get_column_option(column_index,
                                                              TableFormatter.COL_OPT_HEADER_HALIGN).format_string())
                valign_headers.append(self._get_column_option(column_index, TableFormatter.COL_OPT_HEADER_VALIGN))
            halign_cells.append(self._get_column_option(column_index,
                                                        TableFormatter.COL_OPT_CELL_HALIGN).format_string())
            valign_cells.append(self._get_column_option(column_index, TableFormatter.COL_OPT_CELL_VALIGN))

        # get the largest entry width for each column
        # put each field into row structure as lists of lines
        for entry in entries:
            row = list()
            entry_opts = dict()
            if use_attribs:
                # if use_attribs is set, the entries can optionally be a tuple with (object, options)
                try:
                    iter(entry)
                except TypeError:
                    # not iterable, so we just use the object directly
                    entry_obj = entry
                else:

                    if len(entry) == 2:
                        entry_opts = entry[1]
                    entry_obj = entry[0]

                for column_index, attrib_name in enumerate(self._column_attribs):
                    field_obj = None
                    if hasattr(entry_obj, attrib_name):
                        field_obj = getattr(entry_obj, attrib_name, '')
                        # if the object attribute is callable, go ahead and call it and get the result
                        if callable(field_obj):
                            field_obj = field_obj()

                    formatter = self._get_column_option(column_index, TableFormatter.COL_OPT_FIELD_FORMATTER)
                    obj_formatter = self._get_column_option(column_index, TableFormatter.COL_OPT_OBJECT_FORMATTER)
                    if obj_formatter is not None and callable(obj_formatter):
                        field_string = obj_formatter(entry_obj)
                    elif formatter is not None and callable(formatter):
                        field_string = formatter(field_obj)
                    elif isinstance(field_obj, str):
                        field_string = field_obj
                    elif field_obj is not None:
                        field_string = str(field_obj)
                    else:
                        field_string = ''

                    field_lines = field_string.splitlines()
                    # look for widest line in field
                    width = self._field_printable_width(field_lines)

                    # if this width is wider than the current column width, update the current width to fit
                    if width > col_widths[column_index]:
                        col_widths[column_index] = width

                    row.append(field_lines)

            else:
                if len(entry) == len(self._columns) + 1:
                    # if there is exactly 1 more entry than columns, the last one is metadata
                    entry_opts = entry[len(self._columns)]

                for column_index, field in enumerate(entry):
                    # skip extra values beyond the columns configured
                    if column_index < len(self._columns):
                        formatter = self._get_column_option(column_index, TableFormatter.COL_OPT_FIELD_FORMATTER)
                        if formatter is not None and callable(formatter):
                            field_string = formatter(field, )
                        elif isinstance(field, str):
                            field_string = field
                        elif field is not None:
                            field_string = str(field)
                        else:
                            field_string = ''

                        field_lines = field_string.splitlines()
                        # look for widest line in field
                        width = self._field_printable_width(field_lines)

                        # if this width is wider than the current column width, update the current width to fit
                        if width > col_widths[column_index]:
                            col_widths[column_index] = width

                        row.append(field_lines)

            # pad out column entries to column size
            while len(row) < len(self._columns):
                row.append('')

            rows.append(row)
            row_opts.append(entry_opts)

        # if transpose is set, transpose the table now
        if transpose:
            trans_num_cols = len(rows)
            if show_header:
                trans_num_cols += 1

            trans_col_headings = []
            trans_col_widths = [0 for i in range(trans_num_cols)]  # width of each column
            trans_col_max_widths = [0 for i in range(trans_num_cols)]  # maximum width for each column
            trans_rows = []

            # if row headers aren't enabled, generate dummy transpose columns similar to
            # when columns headers are disabled.
            if show_header and not self._global_opts[TableFormatter.TABLE_OPT_ROW_HEADER]:
                trans_col_headings = [str(i) for i in range(trans_num_cols)]

            # every column will now be a row, so we start by looping through columns
            for column_index, column in enumerate(self._columns):
                trans_row = []

                # if we were showing headers, now the header is the first row field
                header_offset = 0
                if self._show_header:
                    trans_row.append(col_headings[column_index])

                    header_width = self._field_printable_width(col_headings[column_index])
                    if trans_col_widths[0] < header_width:
                        trans_col_widths[0] = header_width

                    header_offset = 1

                # loop through every row, append to the current row the field for that column
                for row_index, row in enumerate(rows):
                    field = row[column_index]
                    trans_row.append(field)

                    # re-measure all of the col widths
                    field_width = self._field_printable_width(field)
                    if trans_col_widths[row_index + header_offset] < field_width:
                        trans_col_widths[row_index + header_offset] = field_width

                if column_index == 0 and self._global_opts[TableFormatter.TABLE_OPT_ROW_HEADER]:
                    trans_col_headings = trans_row
                else:
                    trans_rows.append(trans_row)

            col_headings = trans_col_headings
            col_widths = trans_col_widths
            col_max_widths = trans_col_max_widths
            rows = trans_rows
            halign_cells.insert(0, '>')
            valign_cells.insert(0, ColumnAlignment.AlignTop)

            show_header = self._global_opts[TableFormatter.TABLE_OPT_ROW_HEADER]
            show_row_header = self._show_header

        # trim all of the col_widths back to col_max_width
        for column_index in range(0, len(col_widths)):
            if 0 < col_max_widths[column_index] < col_widths[column_index]:
                col_widths[column_index] = col_max_widths[column_index]

        if show_header:
            # wrap all headings that exceed col_width
            header_lines = 1
            for column_index, col_heading in enumerate(col_headings):
                if _printable_width(col_heading[0]) > col_max_widths[column_index] > 0:
                    col_headings[column_index] = _text_wrap(col_heading[0], width=col_max_widths[column_index])
                if len(col_headings[column_index]) > header_lines:
                    header_lines = len(col_headings[column_index])

        row_counts = []  # number of lines for each table now
        # wrap all fields that exceed col_width
        for row_index, row in enumerate(rows):
            row_count = 1
            for col_index, field in enumerate(row):
                field_entry = []
                # iterate through all lines of field
                for field_line, field_line_text in enumerate(field):
                    # if any line of the field exceeds
                    line_length = _printable_width(field_line_text)
                    line_max = col_max_widths[col_index]
                    if line_length > line_max > 0:
                        wrap_mode = self._get_column_option(col_index, TableFormatter.COL_OPT_WRAP_MODE)
                        if wrap_mode == WrapMode.WRAP:
                            field_entry.extend(_text_wrap(field_line_text, width=line_max))
                        elif wrap_mode == WrapMode.WRAP_WITH_INDENT:
                            prefix = self._get_column_option(col_index, TableFormatter.COL_OPT_WRAP_INDENT_PREFIX)
                            wrapper = _TableTextWrapper(width=line_max,
                                                        subsequent_indent=prefix)
                            field_entry.extend(wrapper.wrap(field_line_text))
                        elif wrap_mode == WrapMode.TRUNCATE_END:
                            field_entry.append(field_line_text[:(line_max - 3)] + '...')
                        elif wrap_mode == WrapMode.TRUNCATE_FRONT:
                            field_entry.append('...' + field_line_text[line_length - line_max + 3:])
                        elif wrap_mode == WrapMode.TRUNCATE_MIDDLE:
                            field_entry.append(field_line_text[: (line_max - 5) // 2] + ' ... ' +
                                               field_line_text[line_length - ((line_max - 5) // 2):])
                        elif wrap_mode == WrapMode.TRUNCATE_HARD:
                            field_entry.append(field_line_text[:line_max])
                        else:
                            field_entry.extend(_text_wrap(field_line_text, width=line_max))
                    else:
                        field_entry.append(field_line_text)

                # store the wrapped lines back into the field
                row[col_index] = field_entry
                # if the new line count is higher than the highest known for the row, update it
                if len(field_entry) > row_count:
                    row_count = len(field_entry)
            row_counts.append(row_count)

        # ======= build column headers ========

        out_string = ''
        # build top border
        if self._grid_style.border_top:
            if self._grid_style.border_left:
                out_string += self._grid_style.border_top_left
            for column_index, width in enumerate(col_widths):
                if column_index > 0 and self._grid_style.col_divider:
                    if column_index == 1 and show_row_header:
                        out_string += self._grid_style.border_top_header_col_divider
                    else:
                        out_string += self._grid_style.border_top_col_divider
                pad_width = self._get_column_option(column_index, TableFormatter.COL_OPT_CELL_PADDING)
                out_string += '{0:{pad}<{width}}'.format('',
                                                         pad=self._grid_style.border_top_span,
                                                         width=width + (2 * pad_width))
            if self._grid_style.border_right:
                out_string += self._grid_style.border_top_right
            out_string += '\n'

        if show_header:
            # fill in header text
            for heading_line in range(0, header_lines):
                # for each line of the header
                if self._grid_style.border_left:
                    out_string += self._grid_style.border_left_span(None)

                # for each column to display
                for column_index, col_heading in enumerate(col_headings):
                    if column_index > 0 and self._grid_style.col_divider:
                        if column_index == 1 and show_row_header:
                            out_string += self._grid_style.header_col_divider_span(None)
                        else:
                            out_string += self._grid_style.col_divider_span(None)
                    pad_string = self._get_pad_string(column_index)
                    out_string += pad_string

                    # add the line of the column
                    mapped_line = heading_line
                    if len(col_heading) != header_lines:
                        if valign_headers[column_index] == ColumnAlignment.AlignTop:
                            mapped_line = heading_line
                        elif valign_headers[column_index] == ColumnAlignment.AlignBottom:
                            mapped_line = heading_line - (header_lines - len(col_heading))
                        else:
                            mapped_line = heading_line - int((header_lines - len(col_heading)) / 2)

                    if len(col_heading) > mapped_line >= 0:
                        heading_line_text = _pad_columns(col_heading[mapped_line],
                                                         pad_char=self._grid_style.cell_pad_char,
                                                         align=halign_headers[column_index],
                                                         width=col_widths[column_index])
                        out_string += TableColors.BOLD + heading_line_text + TableColors.RESET
                    else:
                        out_string += '{0:{pad}<{width}}'.format('',
                                                                 pad=self._grid_style.cell_pad_char,
                                                                 width=col_widths[column_index])
                    out_string += pad_string

                if self._grid_style.border_right:
                    out_string += self._grid_style.border_right_span(None)
                out_string += '\n'

            # build header divider
            if self._grid_style.border_header_divider:
                if self._grid_style.border_left:
                    out_string += self._grid_style.border_left_header_divider
                for column_index, width in enumerate(col_widths):
                    if column_index > 0 and self._grid_style.col_divider:
                        if column_index == 1 and show_row_header:
                            out_string += self._grid_style.border_header_header_col_divider
                        else:
                            out_string += self._grid_style.border_header_col_divider
                    pad_width = self._get_column_option(column_index, TableFormatter.COL_OPT_CELL_PADDING)
                    out_string += '{0:{pad}<{width}}'.format('',
                                                             pad=self._grid_style.border_header_divider_span,
                                                             width=width + (2 * pad_width))
                if self._grid_style.border_right:
                    out_string += self._grid_style.border_right_header_divider
                out_string += '\n'

        # ========== add entries ==========
        for row_index, row in enumerate(rows):
            # add row divider (only after the first row)
            if row_index > 0 and self._grid_style.row_divider:
                if self._grid_style.border_left:
                    out_string += self._grid_style.border_left_row_divider
                for col_index, width in enumerate(col_widths):
                    if col_index > 0 and self._grid_style.col_divider:
                        if col_index == 1 and show_row_header:
                            out_string += self._grid_style.row_divider_header_col_divider
                        else:
                            out_string += self._grid_style.row_divider_col_divider
                    pad_width = self._get_column_option(col_index, TableFormatter.COL_OPT_CELL_PADDING)
                    out_string += '{0:{pad}<{width}}'.format('',
                                                             pad=self._grid_style.row_divider_span,
                                                             width=width + (2 * pad_width))
                if self._grid_style.border_right:
                    out_string += self._grid_style.border_right_row_divider
                out_string += '\n'

            # loop for each line in the row
            num_lines = row_counts[row_index]
            for row_line in range(0, num_lines):
                if self._grid_style.border_left:
                    out_string += self._grid_style.border_left_span(row_index)
                # for each column in the row
                for col_index, field in enumerate(row):
                    # if it's not the first column, add a column divider
                    if col_index > 0 and self._grid_style.col_divider:
                        if col_index == 1 and show_row_header:
                            out_string += self._grid_style.header_col_divider_span(row_index)
                        else:
                            out_string += self._grid_style.col_divider_span(row_index)

                    pad_string = self._get_pad_string(col_index)
                    out_string += pad_string

                    mapped_line = row_line
                    if len(field) != num_lines:
                        if valign_cells[col_index] == ColumnAlignment.AlignTop:
                            mapped_line = row_line
                        elif valign_cells[col_index] == ColumnAlignment.AlignBottom:
                            mapped_line = row_line - (num_lines - len(field))
                        else:
                            mapped_line = row_line - int((num_lines - len(field)) / 2)

                    opts = dict()
                    if len(field) > mapped_line >= 0:
                        row_line_text = field[mapped_line]
                        if row_index < len(row_opts):
                            opts = row_opts[row_index]
                        # if the field has a line for the current row line, add it
                    else:
                        row_line_text = ''
                    row_line_text = _pad_columns(row_line_text,
                                                 pad_char=self._grid_style.cell_pad_char,
                                                 align=halign_cells[col_index],
                                                 width=col_widths[col_index])

                    if TableFormatter.ROW_OPT_TEXT_COLOR in opts.keys():
                        row_line_text = opts[TableFormatter.ROW_OPT_TEXT_COLOR] + row_line_text
                    out_string += row_line_text
                    out_string += pad_string + TableColors.RESET

                if self._grid_style.border_right:
                    out_string += self._grid_style.border_right_span(row_index)
                out_string += '\n'

        # close table
        if self._grid_style.border_bottom:
            if self._grid_style.border_left:
                out_string += self._grid_style.border_bottom_left

            for col_index, width in enumerate(col_widths):
                if col_index > 0 and self._grid_style.col_divider:
                    if col_index == 1 and show_row_header:
                        out_string += self._grid_style.border_bottom_header_col_divider
                    else:
                        out_string += self._grid_style.border_bottom_col_divider
                pad_width = self._get_column_option(col_index, TableFormatter.COL_OPT_CELL_PADDING)

                out_string += '{0:{pad}<{width}}'.format('',
                                                         pad=self._grid_style.border_bottom_span,
                                                         width=width + (2 * pad_width))
            if self._grid_style.border_right:
                out_string += self._grid_style.border_bottom_right
            out_string += '\n'

        return out_string

    @staticmethod
    def _field_printable_width(field_lines):
        width = 0
        for field_line in field_lines:
            if _printable_width(field_line) > width:
                width = _printable_width(field_line)

        return width

    def _resolve_column_index(self, column: Union[int, str]):
        """
        Detect if column is a name or an index. If it's a name, convert to index
        :param column: name or index
        :return: column index
        """
        if isinstance(column, str):
            try:
                column_index = self._column_names.index(column)
            except ValueError:
                raise ValueError('Invalid column name: ' + column)
            else:
                column = column_index
        return column

    def _get_column_option(self, column: Union[int, str], option_name: str):
        col_index = self._resolve_column_index(column)
        if col_index in self._column_opts.keys():
            options = self._column_opts[col_index]
            if option_name in options.keys():
                return options[option_name]
        if option_name in self._global_opts.keys():
            return self._global_opts[option_name]
        return None

    def _set_column_option(self, column: Union[int, str], option_name: str, value):
        column = self._resolve_column_index(column)
        if 0 <= column < len(self._columns):
            if column not in self._column_opts.keys():
                self._column_opts[column] = {}
            self._column_opts[column][option_name] = value
        else:
            raise IndexError('Invalid column position: ' + str(column))

    def _get_pad_string(self, column: Union[int, str]):
        pad_width = self._get_column_option(column, TableFormatter.COL_OPT_CELL_PADDING)
        if pad_width > 0:
            return '{0:{cell_padding}}'.format('', cell_padding=pad_width)
        return ''


class FormatBytes:
    """Formats a value in bytes into a human readable string"""
    KB = 1024
    MB = KB * 1024
    GB = MB * 1024
    TB = GB * 1024

    def __call__(self, byte_size: int):
        """
        Formats a value in bytes into a human readable string
        :param byte_size: size in bytes
        :return: human-readable string
        """
        if byte_size is None:
            return ''
        if not isinstance(byte_size, int):
            try:
                byte_size = int(byte_size)
            except ValueError:
                return ''

        decimal_format = '{:.02f}'
        if byte_size > FormatBytes.TB:
            out = decimal_format.format(byte_size / FormatBytes.TB) + " TB"
        elif byte_size > FormatBytes.GB:
            out = decimal_format.format(byte_size / FormatBytes.GB) + " GB"
        elif byte_size > FormatBytes.MB:
            out = decimal_format.format(byte_size / FormatBytes.MB) + " MB"
        elif byte_size > FormatBytes.KB:
            out = decimal_format.format(byte_size / FormatBytes.KB) + " KB"
        else:
            out = decimal_format.format(byte_size) + " B"

        return out


class FormatCommas:
    """Formats a number with comma separators"""
    def __call__(self, number: Union[int, str]):
        if number is None:
            return ''
        if isinstance(number, str):
            number = int(number)
        return format(number, ',d')
