# coding=utf-8
# flake8: noqa F401
from .colors import TableColors
from .constants import DEFAULT_GRID, set_default_grid
from .formatters import FormatBytes, FormatCommas
from .grids import FancyGrid, SparseGrid, AlternatingRowGrid, Grid
from .model import Column, Row, ColumnAlignment, Options, WrapMode
from .tableformatter import TableFormatter
from .typing_wrapper import Iterable, Union, Collection, Tuple, Optional, Callable

import itertools


def generate_table(rows: Iterable[Union[Iterable, object]],
                   columns: Collection[Union[str, Tuple[str, dict]]] = None,
                   *,
                   grid_style: Optional[Grid] = None,
                   transpose: bool = False,
                   row_tagger: Callable = None) -> str:
    """
    Convenience function to easily generate a table from rows/columns

    Rows can be one of the following special cases:
        1. A single dict - in this case, the dictionary keys will become column headers and the dictionary values will
           be placed in a single row to be displayed
        2. numpy record array - if no columns specified, attempt to automatically generate columns from numpy data type
           object specification.
        3. pandas data frame - extract the rows from the pandas object. If not columns specified, extract the columns
           from the pandas object.
           TODO: verify behavior when columns are provided

    Normal rows types:
        1. iterable of iterable - generally a list of lists or tuples. Columns are indexed by the index of the inner
                                  list/tuple
        2. iterable of dicts - dictionary keys will be used to look up values. If no columns are specified, the keys
                               from the first entry will be used.
        3. iterable of objects - all columns must provide a specified attrib to extract values. Inspect object for
                                 an attrib matching the specified attrib name. If attrib is a property, fetch property
                                 and call str() on it. If it's a function, call the function with no parameters.


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

            # TODO: revisit this, if columns is specified the row values won't match the columns. Should consider one
            #       of the following solutions:
            #       1. Construct the row based on the columns column name or attrib specified as dictionary key
            #       2. Place values into a named tuple that can be accessed by attrib name
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
