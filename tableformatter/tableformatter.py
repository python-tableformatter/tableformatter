# coding=utf-8
"""
Formats data into a table.


Steps:
Detect input: Categorize input into known types (List of lists of strings, list of objects, list of dicts)
Normalize Column Specifier: Process column specifiers into standard ColumnSpec objects.
Extract/Normalize Data: Inspect input, call functions if needed, store raw data in a standard RowObject/CellObject
                        RowObject should retain reference to original input row without modification.
                        If column specifier has a obj_formatter - generate cell data with obj_formatter
Decorate RowObject: If row decorator provided, decorate row object
Decorate Cells: Call column and row decorator functions and decorate each cell with metadata
Render Data to String: Check each cell for its formatter function to render raw data into strings. Track max string width
Transpose Data: if specified
Align/wrap cell text: using column wrapping properties or custom wrapping function,
Render table: apply per-cell properties
"""
from .colors import TableColors
from .constants import DEFAULT_GRID
from .model import WrapMode, ColumnAlignment, Options, ColumnObject
from .text_utils import _text_wrap, _printable_width, _TableTextWrapper, _pad_columns
from .typing_wrapper import Iterable, Tuple, Union, Callable, Collection, List


__version__ = '0.2.0'
ELLIPSIS = '…'


class TableFormatter(object):
    """
    Simple implementation of an ascii table formatter.
    Allows definition of max column width
    Allows definition of custom cell format functions
    """

    def __init__(self,
                 columns: Collection[Union[ColumnObject, str, Tuple[str, dict]]],
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
        self._global_opts = {Options.COL_OPT_HEADER_HALIGN: default_header_horiz_align,
                             Options.COL_OPT_HEADER_VALIGN: default_header_vert_align,
                             Options.COL_OPT_CELL_HALIGN: default_cell_horiz_align,
                             Options.COL_OPT_CELL_VALIGN: default_cell_vert_align,
                             Options.COL_OPT_WIDTH: max_column_width,
                             Options.COL_OPT_CELL_PADDING: cell_padding,
                             Options.COL_OPT_WRAP_MODE: WrapMode.WRAP,
                             Options.COL_OPT_WRAP_INDENT_PREFIX: ' » ',
                             Options.COL_OPT_ATTRIB_NAME: use_attribs,
                             Options.TABLE_OPT_TRANSPOSE: transpose,
                             Options.TABLE_OPT_ROW_HEADER: row_show_header}
        self._show_header = show_header
        self._row_tagger = row_tagger

        for col_index, column in enumerate(columns):
            if isinstance(column, tuple) and len(column) > 1 and isinstance(column[1], dict):
                self._column_names.append(column[0])
                self._column_opts[col_index] = column[1]

                if use_attribs and Options.COL_OPT_ATTRIB_NAME in self._column_opts[col_index].keys():
                    self._column_attribs[col_index] = self._column_opts[col_index][Options.COL_OPT_ATTRIB_NAME]

            elif isinstance(column, str):
                self._column_names.append(column)
            else:
                self._column_names.append(str(column))

        if use_attribs:
            for col_ind, attrib in enumerate(self._column_attribs):
                if attrib is None and Options.COL_OPT_OBJECT_FORMATTER not in self._column_opts[col_ind]:
                    raise ValueError('Attribute name or Object formatter required for {}'.format(self._column_names[col_ind]))

    def set_default_header_alignment(self,
                                     horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                                     vert_align: ColumnAlignment = ColumnAlignment.AlignBottom):
        """
        Set the default header alignment for all columns
        :param horiz_align:
        :param vert_align:
        """
        self._global_opts[Options.COL_OPT_HEADER_HALIGN] = horiz_align
        self._global_opts[Options.COL_OPT_HEADER_VALIGN] = vert_align

    def set_default_cell_alignment(self,
                                   horiz_align: ColumnAlignment = ColumnAlignment.AlignLeft,
                                   vert_align: ColumnAlignment = ColumnAlignment.AlignTop):
        """
        Set the default cell alignment for all columns
        :param horiz_align:
        :param vert_align
        """
        self._global_opts[Options.COL_OPT_CELL_HALIGN] = horiz_align
        self._global_opts[Options.COL_OPT_CELL_VALIGN] = vert_align

    def set_formatter(self, column: Union[int, str], format_function):
        """
        Optionally specify a custom format function for a column index
        :param column: column position this applies to
        :param format_function: function to call to format the value. Signature: def myfunction(field_value):
        """
        self._set_column_option(column, Options.COL_OPT_FIELD_FORMATTER, format_function)

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
        self._set_column_option(column, Options.COL_OPT_HEADER_HALIGN, horiz_align)
        self._set_column_option(column, Options.COL_OPT_HEADER_VALIGN, vert_align)

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
        self._set_column_option(column, Options.COL_OPT_CELL_HALIGN, horiz_align)
        self._set_column_option(column, Options.COL_OPT_CELL_VALIGN, vert_align)

    # TODO: Reduce the cyclomatic complexity of generate_table which is currently at 106!
    # flake8: noqa F401
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
        use_attribs = self._global_opts[Options.COL_OPT_ATTRIB_NAME]
        transpose = self._global_opts[Options.TABLE_OPT_TRANSPOSE] or force_transpose
        show_header = self._show_header and (self._grid_style.show_header or transpose)
        show_row_header = self._global_opts[Options.TABLE_OPT_ROW_HEADER]

        # combine formatter defaults and specifiers
        for column_index, column in enumerate(self._columns):
            # identify the max width for the column

            max_width = self._get_column_option(column_index, Options.COL_OPT_WIDTH)
            col_max_widths[column_index] = max_width

            if show_header:
                col_heading = self._column_names[column_index]
                col_headings.append([col_heading])
                col_widths[column_index] = _printable_width(col_heading)

                halign_headers.append(self._get_column_option(column_index,
                                                              Options.COL_OPT_HEADER_HALIGN).format_string())
                valign_headers.append(self._get_column_option(column_index, Options.COL_OPT_HEADER_VALIGN))
            halign_cells.append(self._get_column_option(column_index,
                                                        Options.COL_OPT_CELL_HALIGN).format_string())
            valign_cells.append(self._get_column_option(column_index, Options.COL_OPT_CELL_VALIGN))

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
                        entry_obj = entry[0]
                        if self._row_tagger is not None:
                            entry_opts = self._row_tagger(entry_obj)
                        if len(entry) == 2 and isinstance(entry[1], dict):
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

                    formatter = self._get_column_option(column_index, Options.COL_OPT_FIELD_FORMATTER)
                    obj_formatter = self._get_column_option(column_index, Options.COL_OPT_OBJECT_FORMATTER)
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
                        formatter = self._get_column_option(column_index, Options.COL_OPT_FIELD_FORMATTER)
                        obj_formatter = self._get_column_option(column_index, Options.COL_OPT_OBJECT_FORMATTER)
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
            if show_header and not self._global_opts[Options.TABLE_OPT_ROW_HEADER]:
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

                if column_index == 0 and self._global_opts[Options.TABLE_OPT_ROW_HEADER]:
                    trans_col_headings = trans_row
                else:
                    trans_rows.append(trans_row)

            col_headings = trans_col_headings
            col_widths = trans_col_widths
            col_max_widths = trans_col_max_widths
            rows = trans_rows
            halign_cells.insert(0, '>')
            valign_cells.insert(0, ColumnAlignment.AlignTop)

            show_header = self._global_opts[Options.TABLE_OPT_ROW_HEADER]
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
                        wrap_mode = self._get_column_option(col_index, Options.COL_OPT_WRAP_MODE)
                        if wrap_mode == WrapMode.WRAP:
                            field_entry.extend(_text_wrap(field_line_text, width=line_max))
                        elif wrap_mode == WrapMode.WRAP_WITH_INDENT:
                            prefix = self._get_column_option(col_index, Options.COL_OPT_WRAP_INDENT_PREFIX)
                            wrapper = _TableTextWrapper(width=line_max,
                                                        subsequent_indent=prefix)
                            field_entry.extend(wrapper.wrap(field_line_text))
                        elif wrap_mode == WrapMode.TRUNCATE_END:
                            ell_len = _printable_width(ELLIPSIS)
                            field_entry.append(field_line_text[:(line_max - ell_len)] + ELLIPSIS)
                        elif wrap_mode == WrapMode.TRUNCATE_FRONT:
                            ell_len = _printable_width(ELLIPSIS)
                            field_entry.append(ELLIPSIS + field_line_text[line_length - line_max + ell_len:])
                        elif wrap_mode == WrapMode.TRUNCATE_MIDDLE:
                            ell_len = _printable_width(ELLIPSIS) + 2
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
                pad_width = self._get_column_option(column_index, Options.COL_OPT_CELL_PADDING)
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
                    pad_width = self._get_column_option(column_index, Options.COL_OPT_CELL_PADDING)
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
                    pad_width = self._get_column_option(col_index, Options.COL_OPT_CELL_PADDING)
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

                    colorize = len(row_line_text.strip()) > 0 and Options.ROW_OPT_TEXT_COLOR in opts.keys()

                    row_line_text = _pad_columns(row_line_text,
                                                 pad_char=self._grid_style.cell_pad_char,
                                                 align=halign_cells[col_index],
                                                 width=col_widths[col_index])

                    if colorize:
                        row_line_text = opts[Options.ROW_OPT_TEXT_COLOR] + row_line_text
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
                pad_width = self._get_column_option(col_index, Options.COL_OPT_CELL_PADDING)

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
        pad_width = self._get_column_option(column, Options.COL_OPT_CELL_PADDING)
        if pad_width > 0:
            return '{0:{cell_padding}}'.format('', cell_padding=pad_width)
        return ''

    def _normalize_columns(self, columns: Collection[Union[ColumnObject, str, Tuple[str, dict]]]) -> List[ColumnObject]:
        out = []
        for index, column in enumerate(columns):
            if isinstance(column, ColumnObject):
                column.set_table(self, index)
                out.append(column)
            elif isinstance(column, str):
                out.append(ColumnObject(self, index, column))
            elif isinstance(column, Tuple) and\
                    len(column) == 2 and\
                    isinstance(column[0], str) and\
                    isinstance(column[1], dict):
                col_obj = ColumnObject(self, index, column[0], **(column[1]))
                out.append(col_obj)
            else:
                out.append(ColumnObject(self, index, str(column)))
        return out
