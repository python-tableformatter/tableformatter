# coding=utf-8
from .colors import TableColors
from .formatters import FormatBytes, FormatCommas
from .grids import FancyGrid, SparseGrid, AlternatingRowGrid, Grid
from .model import Column, Row, ColumnAlignment, Options, WrapMode
from .tableformatter import TableFormatter
from .typing_wrapper import Iterable, Union, Collection, Tuple, Optional, Callable

import itertools


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
                if Options.COL_OPT_ATTRIB_NAME in column[1].keys():
                    # Does this column specify an object attribute to use?
                    attrib = column[1][Options.COL_OPT_ATTRIB_NAME]
                    if isinstance(attrib, str) and len(attrib) > 0:
                        attrib_count += 1
                elif Options.COL_OPT_OBJECT_FORMATTER in column[1].keys():
                    # If no column attribute, does this column have an object formatter?
                    func = column[1][Options.COL_OPT_OBJECT_FORMATTER]
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