# coding=utf-8
"""
Formats data into a table
"""
import abc
import enum
import itertools
import re
import textwrap as textw
from typing import List, Iterable, Optional, Tuple, Union, Callable, Sequence

from wcwidth import wcswidth

# This whole try/except exists to make sure a Collection type exists for use with optional type hinting and isinstance
try:
    # Python 3.6+ should have Collection in the typing module
    from typing import Collection
except ImportError:
    from typing import Container, Generic, Sized, TypeVar

    T_co = TypeVar('T_co', covariant=True)
    # Python 3.5
    # noinspection PyAbstractClass
    class Collection(Generic[T_co], Container, Sized, Iterable):
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
__version__ = '0.1.4'
ELLIPSIS = '…'


def _text_wrap(text: str, width: int=70) -> List[str]:
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

    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width):
        """_handle_long_word(chunks : [string],
                             cur_line : [string],
                             cur_len : int, width : int)

        Handle a chunk of text (most likely a word, not whitespace) that
        is too long to fit in any line.
        """
        # Figure out when indent is larger than the specified width, and make
        # sure at least one character is stripped off on every pass
        if width < 1:
            space_left = 1
        else:
            space_left = width - cur_len

        # If we're allowed to break long words, then do so: put as much
        # of the next chunk onto the current line as will fit.
        if self.break_long_words:
            shard_length = space_left
            shard = reversed_chunks[-1][:shard_length]
            while _wcswidth(shard) > space_left and shard_length > 0:
                shard_length -= 1
                shard = reversed_chunks[-1][:shard_length]
            if shard_length > 0:
                cur_line.append(shard)
                reversed_chunks[-1] = reversed_chunks[-1][shard_length:]

        # Otherwise, we have to preserve the long word intact.  Only add
        # it to the current line if there's nothing already there --
        # that minimizes how much we violate the width constraint.
        elif not cur_line:
            cur_line.append(reversed_chunks.pop())

        # If we're not allowed to break long words, and there's already
        # text on the current line, do nothing.  Next time through the
        # main loop of _wrap_chunks(), we'll wind up here again, but
        # cur_len will be zero, so the next line will be entirely
        # devoted to the long word that we can't handle right now.

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
                length = _wcswidth(chunks[-1])

                # Can at least squeeze this chunk onto the current line.
                if cur_len + length <= width:
                    cur_line.append(chunks.pop())
                    cur_len += length

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
                if (self.max_lines is None or len(lines) + 1 < self.max_lines
                        or (not chunks or self.drop_whitespace and len(chunks) == 1 and not chunks[0].strip())
                        and cur_len <= width):
                    # Convert current line back to a string and store it in
                    # list of all lines (return value).
                    lines.append(indent + ''.join(cur_line))
                else:
                    while cur_line:
                        if cur_line[-1].strip() and cur_len + _wcswidth(self.placeholder) <= width:
                            cur_line.append(self.placeholder)
                            lines.append(indent + ''.join(cur_line))
                            break
                        cur_len -= _wcswidth(cur_line[-1])
                        del cur_line[-1]
                    else:
                        if lines:
                            prev_line = lines[-1].rstrip()
                            if _wcswidth(prev_line) + _wcswidth(self.placeholder) <= self.width:
                                lines[-1] = prev_line + self.placeholder
                                break
                        lines.append(indent + self.placeholder.lstrip())
                    break

        return lines


def _translate_tabs(text: str) -> str:
    """Translate tab characters into spaces for measurement"""
    tabpos = text.find('\t')
    while tabpos >= 0:
        before_text = text[:tabpos]
        after_text = text[tabpos + 1:]
        before_width = _wcswidth(before_text)
        tab_pad = TAB_WIDTH - (before_width % TAB_WIDTH)
        text = before_text + '{: <{width}}'.format('', width=tab_pad) + after_text

        tabpos = text.find('\t')
    return text


def _printable_width(text: str) -> int:
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
        BG_COLOR_ROW = bg(244)
        BG_RESET = attr('reset')  # docs say bg(0) should do this but it doesn't work right
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
            RESET = Style.NORMAL + Fore.RESET + Back.RESET
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
            cls.BG_COLOR_ROW = bg(244)
            cls.BG_RESET = attr('reset')  # docs say bg(0) should do this but it doesn't work right
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
            cls.RESET = Style.NORMAL + Fore.RESET + Back.RESET
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
    diff = width - display_width
    if display_width >= width:
        return text

    if align in (ColumnAlignment.AlignLeft, ColumnAlignment.AlignLeft.format_string()):
        out_text = text
        out_text += '{:{pad}<{width}}'.format('', pad=pad_char, width=diff)
    elif align in (ColumnAlignment.AlignRight, ColumnAlignment.AlignRight.format_string()):
        out_text = '{:{pad}<{width}}'.format('', pad=pad_char, width=diff)
        out_text += text
    elif align in (ColumnAlignment.AlignCenter, ColumnAlignment.AlignCenter.format_string()):
        lead_pad = diff // 2
        tail_pad = diff - lead_pad

        out_text = '{:{pad}<{width}}'.format('', pad=pad_char, width=lead_pad)
        out_text += text
        out_text += '{:{pad}<{width}}'.format('', pad=pad_char, width=tail_pad)
    else:
        out_text = text
        out_text += '{:{pad}<{width}}'.format('', pad=pad_char, width=diff)

    return out_text


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


class Grid(abc.ABC):
    """Abstract class representing a table grid which may or may not have lines dividing rows and/or columns."""
    def __init__(self):
        self.can_wrap = True
        self.show_header = False

        self.border_top = False
        self.border_top_left = ''
        self.border_top_span = ''
        self.border_top_right = ''
        self.border_top_col_divider = ''
        self.border_top_header_col_divider = ''

        self.border_header_divider = False
        self.border_left_header_divider = ''
        self.border_right_header_divider = ''
        self.border_header_divider_span = ''
        self.border_header_col_divider = ''
        self.border_header_header_col_divider = ''

        self.border_left = False
        self.border_left_row_divider = ''

        self.border_right = False
        self.border_right_row_divider = ''

        self.col_divider = True
        self.row_divider = False
        self.row_divider_span = ''

        self.row_divider_col_divider = ''
        self.row_divider_header_col_divider = ''

        self.border_bottom = True
        self.border_bottom_left = ''
        self.border_bottom_right = ''
        self.border_bottom_span = ''
        self.border_bottom_col_divider = ''
        self.border_bottom_header_col_divider = ''

        self.cell_pad_char = ' '

    @abc.abstractmethod
    def border_left_span(self, row_index: Union[int, None]) -> str:
        return ''

    @abc.abstractmethod
    def border_right_span(self, row_index: Union[int, None]) -> str:
        return ''

    @abc.abstractmethod
    def col_divider_span(self, row_index: Union[int, None]) -> str:
        return ''

    @abc.abstractmethod
    def header_col_divider_span(self, row_index: Union[int, None]) -> str:
        return ''

    def cell_format(self, text: str) -> str:
        return text


class SparseGrid(Grid):
    """Very basic sparse table grid, without any lines diving rows or columns or alternating row color.

    This conserves both vertical and horizontal space but doesn't look very good in most cases.
    """
    def border_left_span(self, row_index: Union[int, None]) -> str:
        return ''

    def border_right_span(self, row_index: Union[int, None]) -> str:
        return ''

    def col_divider_span(self, row_index: Union[int, None]) -> str:
        return ''

    def header_col_divider_span(self, row_index: Union[int, None]) -> str:
        return ''


class FancyGrid(Grid):
    """Fancy table with grid lines dividing rows and columns.

    This typically looks great, but consumes a lot of extra space both horizontally and vertically.
    """
    def __init__(self):
        super().__init__()
        self.show_header = True
        self.border_top = True

        self.border_top_left = '╔'
        self.border_top_span = '═'
        self.border_top_right = '╗'
        self.border_top_col_divider = '╤'
        self.border_top_header_col_divider = '╦'

        self.border_header_divider = True
        self.border_left_header_divider = '╠'
        self.border_right_header_divider = '╣'
        self.border_header_divider_span = '═'
        self.border_header_col_divider = '╪'
        self.border_header_header_col_divider = '╬'

        self.border_left = True
        self.border_left_row_divider = '╟'

        self.border_right = True
        self.border_right_row_divider = '╢'

        self.col_divider = True
        self.row_divider = True
        self.row_divider_span = '─'

        self.row_divider_col_divider = '┼'
        self.row_divider_header_col_divider = '╫'

        self.border_bottom = True
        self.border_bottom_left = '╚'
        self.border_bottom_right = '╝'
        self.border_bottom_span = '═'
        self.border_bottom_col_divider = '╧'
        self.border_bottom_header_col_divider = '╩'

    def border_left_span(self, row_index: Union[int, None]) -> str:
        return '║'

    def border_right_span(self, row_index: Union[int, None]) -> str:
        return '║'

    def col_divider_span(self, row_index: Union[int, None]) -> str:
        return '│'

    def header_col_divider_span(self, row_index: Union[int, None]) -> str:
        return '║'


class AlternatingRowGrid(FancyGrid):
    """Generates alternating black/gray background colors for rows but still has lines between cols and in header.

    This typically looks quite good, but also does a good job of conserving vertical space.
    """
    def __init__(self, bg_primary: str=None, bg_alternate: str=None, bg_reset=None) -> None:
        """Initialize the AlternatingRowGrid with the two alternating colors.

        :param bg_primary: string reprsenting the primary background color starting with the 1st row
        :param bg_alternate: string representing the alternate background color starting with the 2nd row
        """
        super().__init__()
        # Disable row dividers present in FancyGrid in order to save vertical space
        self.row_divider = False
        self.row_divider_span = ''
        self.row_divider_col_divider = ''
        self.row_divider_header_col_divider = ''
        self.bg_primary = bg_primary
        self.bg_alt = bg_alternate
        self.bg_reset = bg_reset

    def border_left_span(self, row_index: Union[int, None]) -> str:
        bg_reset = self.bg_reset if self.bg_reset is not None else TableColors.BG_RESET
        bg_primary = self.bg_primary if self.bg_primary is not None else TableColors.BG_RESET
        bg_alt = self.bg_alt if self.bg_alt is not None else TableColors.BG_COLOR_ROW

        prefix = bg_reset + '║'
        color = bg_reset
        if isinstance(row_index, int):
            if row_index % 2 == 0:
                color = bg_primary
            else:
                color = bg_alt
        return prefix + color

    def border_right_span(self, row_index: Union[int, None]) -> str:
        bg_reset = self.bg_reset if self.bg_reset is not None else TableColors.BG_RESET
        return bg_reset + '║'

    def col_divider_span(self, row_index: Union[int, None]) -> str:
        bg_reset = self.bg_reset if self.bg_reset is not None else TableColors.BG_RESET
        bg_primary = self.bg_primary if self.bg_primary is not None else TableColors.BG_RESET
        bg_alt = self.bg_alt if self.bg_alt is not None else TableColors.BG_COLOR_ROW

        color = bg_reset
        if isinstance(row_index, int):
            if row_index % 2 == 0:
                color = bg_primary
            else:
                color = bg_alt
        return color + '│'

    def header_col_divider_span(self, row_index: Union[int, None]) -> str:
        bg_reset = self.bg_reset if self.bg_reset is not None else TableColors.BG_RESET
        bg_primary = self.bg_primary if self.bg_primary is not None else TableColors.BG_RESET
        bg_alt = self.bg_alt if self.bg_alt is not None else TableColors.BG_COLOR_ROW

        color = bg_reset
        if isinstance(row_index, int):
            if row_index % 2 == 0:
                color = bg_primary
            else:
                color = bg_alt
        return color + '║'


DEFAULT_GRID = AlternatingRowGrid()


def set_default_grid(grid: Grid) -> None:
    global DEFAULT_GRID
    if grid is not None:
        DEFAULT_GRID = grid


def generate_table(rows: Iterable[Union[Iterable, object]],
                   columns: Collection[Union[str, Tuple[str, dict]]]=None,
                   grid_style: Optional[Grid]=None,
                   transpose: bool=False,
                   row_tagger: Callable=None) -> str:
    """
    Convenience function to easily generate a table from rows/columns

    :param rows: iterable of objects or iterable fields
    :param columns: Iterable of column definitions
    :param grid_style: The grid style to use
    :param transpose: Transpose the rows/columns for display
    :param row_tagger: decorator function to apply per-row options
    :return: formatted string containing the table
    """
    # If a dictionary is passed in, then treat keys as column headers and values as column values
    if isinstance(rows, dict):
        if not columns:
            columns = rows.keys()
        rows = list(itertools.zip_longest(*rows.values()))  # columns have to be transposed

    # Extract column headers if this is a NumPy record array and columns weren't specified
    if not columns:
        try:
            import numpy as np
        except ImportError:
            pass
        else:
            if isinstance(rows, np.recarray):
                columns = rows.dtype.names

    # Deal with Pandas DataFrames not being iterable in a sane way
    try:
        import pandas as pd
    except ImportError:
        pass
    else:
        if isinstance(rows, pd.DataFrame):
            if not columns:
                columns = rows.columns
            rows = rows.values

    show_headers = True
    use_attrib = False
    if isinstance(columns, Collection) and len(columns) > 0:
        columns = list(columns)

        attrib_count = 0
        for column in columns:
            if isinstance(column, tuple) and len(column) > 1 and isinstance(column[1], dict):
                if TableFormatter.COL_OPT_ATTRIB_NAME in column[1].keys():
                    # Does this column specify an object attribute to use?
                    attrib = column[1][TableFormatter.COL_OPT_ATTRIB_NAME]
                    if isinstance(attrib, str) and len(attrib) > 0:
                        attrib_count += 1
                elif TableFormatter.COL_OPT_OBJECT_FORMATTER in column[1].keys():
                    # If no column attribute, does this column have an object formatter?
                    func = column[1][TableFormatter.COL_OPT_OBJECT_FORMATTER]
                    if callable(func):
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
    if grid_style is None:
        grid_style = DEFAULT_GRID
    formatter = TableFormatter(columns, grid_style=grid_style, show_header=show_headers,
                               use_attribs=use_attrib, transpose=transpose, row_tagger=row_tagger)
    return formatter.generate_table(rows)


def Column(col_name: str,
           width: int=None,
           attrib: str=None,
           wrap_mode: WrapMode=None,
           wrap_prefix: str=None,
           cell_padding: int=None,
           header_halign: ColumnAlignment=None,
           header_valign: ColumnAlignment=None,
           cell_halign: ColumnAlignment=None,
           cell_valign: ColumnAlignment=None,
           formatter: Callable=None,
           obj_formatter: Callable=None):
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
        opts[TableFormatter.COL_OPT_WIDTH] = width
    if attrib is not None:
        opts[TableFormatter.COL_OPT_ATTRIB_NAME] = attrib
    if wrap_mode is not None:
        opts[TableFormatter.COL_OPT_WRAP_MODE] = wrap_mode
    if wrap_prefix is not None:
        opts[TableFormatter.COL_OPT_WRAP_INDENT_PREFIX] = wrap_prefix
    if cell_padding is not None:
        opts[TableFormatter.COL_OPT_CELL_PADDING] = cell_padding
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


def Row(*args, text_color: Union[TableColors, str]=None):
    """
    Processes row options and generates a tuple in the format the TableFormatter expects
    :param args: Can be either 1 object or a list of values
    :param text_color: text color to use when displaying this row
    :return: Tuple formatted for the TableFormatter to consume
    """
    opts = dict()

    if text_color is not None:
        opts[TableFormatter.ROW_OPT_TEXT_COLOR] = text_color

    row = list(args)
    if opts:
        row.append(opts)
    return tuple(row)


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
                 grid_style=None,
                 show_header=True,
                 use_attribs=False,
                 transpose=False,
                 row_show_header=False,
                 row_tagger: Callable=None):
        """
        :param columns: list of either column names or tuples of (column name, dict of column options)
        :param cell_padding: number of spaces to pad to the left/right of each column
        """
        self._columns = columns
        if grid_style is None:
            self._grid_style = DEFAULT_GRID
        else:
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
        self._row_tagger = row_tagger

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
                    if TableFormatter.COL_OPT_OBJECT_FORMATTER not in self._column_opts[col_index]:
                        raise ValueError('Attribute name or Object formatter is required for {}'.format(self._column_names[col_index]))

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

    def generate_table(self, entries: Iterable[Union[Iterable, object]], force_transpose=False):
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
                if isinstance(entry, dict):
                    entry_obj = entry
                else:
                    try:
                        iter(entry)
                    except TypeError:
                        # not iterable, so we just use the object directly
                        entry_obj = entry
                        if self._row_tagger is not None:
                            entry_opts = self._row_tagger(entry_obj)
                    else:
                        # check if this is a tuple containing a dictionary of decorated values. If so, the row object
                        # is the first element a the decorated values is the second element.
                        is_tagged = False
                        try:
                            if isinstance(entry, Sequence) and len(entry) == 2 and isinstance(entry[1], dict):
                                entry_obj = entry[0]
                                is_tagged = True
                            else:
                                entry_obj = entry
                        except KeyError:
                            entry_obj = entry
                        if self._row_tagger is not None:
                            entry_opts = self._row_tagger(entry_obj)
                        if is_tagged:
                            entry_opts.update(entry[1])

                for column_index, attrib_name in enumerate(self._column_attribs):
                    field_obj = None
                    if isinstance(attrib_name, str):
                        if hasattr(entry_obj, attrib_name):
                            field_obj = getattr(entry_obj, attrib_name, '')
                        elif isinstance(entry_obj, dict) and attrib_name in entry_obj:
                            field_obj = entry_obj[attrib_name]
                        # if the object attribute is callable, go ahead and call it and get the result
                        if callable(field_obj):
                            field_obj = field_obj()

                    formatter = self._get_column_option(column_index, TableFormatter.COL_OPT_FIELD_FORMATTER)
                    obj_formatter = self._get_column_option(column_index, TableFormatter.COL_OPT_OBJECT_FORMATTER)
                    if obj_formatter is not None and callable(obj_formatter):
                        field_obj = obj_formatter(entry_obj)
                    if formatter is not None and callable(formatter):
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
                if self._row_tagger is not None:
                    entry_opts = self._row_tagger(entry)
                if len(entry) == len(self._columns) + 1 and isinstance(entry[len(self._columns)], dict):
                    # if there is exactly 1 more entry than columns, the last one is metadata
                    entry_opts.update(entry[len(self._columns)])

                for column_index, field in enumerate(entry):
                    # skip extra values beyond the columns configured
                    if column_index < len(self._columns):
                        formatter = self._get_column_option(column_index, TableFormatter.COL_OPT_FIELD_FORMATTER)
                        obj_formatter = self._get_column_option(column_index, TableFormatter.COL_OPT_OBJECT_FORMATTER)
                        if obj_formatter is not None and callable(obj_formatter):
                            field = obj_formatter(entry)
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
                            ell_len = _wcswidth(ELLIPSIS)
                            field_entry.append(field_line_text[:(line_max - ell_len)] + ELLIPSIS)
                        elif wrap_mode == WrapMode.TRUNCATE_FRONT:
                            ell_len = _wcswidth(ELLIPSIS)
                            field_entry.append(ELLIPSIS + field_line_text[line_length - line_max + ell_len:])
                        elif wrap_mode == WrapMode.TRUNCATE_MIDDLE:
                            ell_len = _wcswidth(ELLIPSIS) + 2
                            field_entry.append(field_line_text[: (line_max - ell_len) // 2] + ' ' + ELLIPSIS + ' ' +
                                               field_line_text[line_length - ((line_max - ell_len) // 2):])
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

            opts = dict()
            if row_index < len(row_opts):
                opts = row_opts[row_index]

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

                    if len(field) > mapped_line >= 0:
                        # if the field has a line for the current row line, add it
                        row_line_text = field[mapped_line]
                    else:
                        row_line_text = ''

                    colorize = len(row_line_text.strip()) > 0 and TableFormatter.ROW_OPT_TEXT_COLOR in opts.keys()

                    row_line_text = _pad_columns(row_line_text,
                                                 pad_char=self._grid_style.cell_pad_char,
                                                 align=halign_cells[col_index],
                                                 width=col_widths[col_index])

                    if colorize:
                        row_line_text = opts[TableFormatter.ROW_OPT_TEXT_COLOR] + row_line_text
                    out_string += row_line_text
                    out_string += pad_string
                    if colorize:
                        out_string += TableColors.RESET

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
            out = decimal_format.format(byte_size) + "  B"

        return out


class FormatCommas:
    """Formats a number with comma separators"""
    def __call__(self, number: Union[int, str]):
        if number is None:
            return ''
        if isinstance(number, str):
            number = int(number)
        return format(number, ',d')
