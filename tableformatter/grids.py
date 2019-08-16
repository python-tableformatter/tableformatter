# coding=utf-8
from .colors import TableColors
import abc
from typing import Union


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
