tableformatter: tabular data formatter
======================================
[![Build status](https://api.travis-ci.com/python-tableformatter/tableformatter.svg?branch=master)](https://travis-ci.com/python-tableformatter/tableformatter)
[![codecov](https://codecov.io/gh/python-tableformatter/tableformatter/branch/master/graph/badge.svg)](https://codecov.io/gh/python-tableformatter/tableformatter)

tableformatter is a tabular data formatter allowing printing from both arbitrary tuples of strings or object inspection.
It converts your data into a string form suitable for pretty-printing as a table.  The goal is to make it quick and easy
for developers to display tabular data in an aesthetically pleasing fashion.  It provides a simple public API, but allows
fine-grained control over almost every aspect of how the data is formatted.

Many other modules for formatting tabular data require the developer to create a transition layer to convert their
objects/data into a structure the formatter can consume.  One relatively novel aspect of tableformatter is the ability to directly
receive arbitrary Python objects.

Main Features
-------------
- Easy to display simple tables with just one function call when you don't need the fine-grained control
- Fine-grained control of almost every aspect of how data is formatted when you want it
- Tables with column headers
- Flexible grid style
- Transposed tables with rows and columns swapped
- Colored output using either [colorama](https://github.com/tartley/colorama) or [colored](https://github.com/dslackw/colored)
- Good unicode support including for characters which are more than 1 visual character wide
- Support for Python 3.4+ on Windows, macOS, and Linux


Installation
============
```Bash
pip install tableformatter
```

Dependencies
------------
``tableformatter`` depends on the [wcwidth](https://github.com/jquast/wcwidth) module for measuring the width of 
unicode strings rendered to a terminal.

If you wish to use the optional support for color, then at least one of the following two modules must be installed:
* [colorama](https://github.com/tartley/colorama) - simple cross-platform colored terminal text with about 16 colors
* [colored](https://github.com/dslackw/colored) - library for color in terminal with 256 colors, macOS and Linux only

If both ``colorama`` and ``colored`` are installed, then ``colored`` will take precedence.


Usage
=====
For simple cases, you only need to use a single function from this module: ``generate_table``.  The only required argument
to this function is ``rows`` which is an Iterable of Iterables such as a list of lists or another tabular data type like 
a 2D [numpy](http://www.numpy.org) array.  ``generate_table`` outputs a nicely formatted table:

```Python
>>> from tableformatter import generate_table

>>> rows = [('A1', 'A2', 'A3', 'A4'),
...         ('B1', 'B2\nB2\nB2', 'B3', 'B4'),
...         ('C1', 'C2', 'C3', 'C4'),
...         ('D1', 'D2', 'D3', 'D4')]
>>> print(generate_table(rows))
╔════╤════╤════╤════╗
║ A1 │ A2 │ A3 │ A4 ║
║ B1 │ B2 │ B3 │ B4 ║
║    │ B2 │    │    ║
║    │ B2 │    │    ║
║ C1 │ C2 │ C3 │ C4 ║
║ D1 │ D2 │ D3 │ D4 ║
╚════╧════╧════╧════╝
```

*NOTE: Rendering of tables looks much better in Python than it appears in this Markdown file.*

Column Headers
--------------
The second argument to ``generate_table`` named ``columns`` is optional and defines a list of column headers to be used.

```Python
>>> cols = ['Col1', 'Col2', 'Col3', 'Col4']
>>> print(generate_table(rows, cols))
╔══════╤══════╤══════╤══════╗
║ Col1 │ Col2 │ Col3 │ Col4 ║
╠══════╪══════╪══════╪══════╣
║ A1   │ A2   │ A3   │ A4   ║
║ B1   │ B2   │ B3   │ B4   ║
║      │ B2   │      │      ║
║      │ B2   │      │      ║
║ C1   │ C2   │ C3   │ C4   ║
║ D1   │ D2   │ D3   │ D4   ║
╚══════╧══════╧══════╧══════╝
```

Grid Style
----------
The third argument to ``generated`` table named ``grid_style`` is optional and specifies how the table lines are drawn.

Supported grid sytles are:

* **AlternatingRowGrid** - generates alternating black/gray background colors for rows to conserve vertical space (defalt)
* **FancyGrid** - fancy table with grid lines dividing rows and columns
* **SparseGrid** - sparse grid with no lines at all to conserve both vertical and horizontal space

```Python
>>> from tableformatter import FancyGrid

>>> print(generate_table(rows, grid_style=FancyGrid))
╔════╤════╤════╤════╗
║ A1 │ A2 │ A3 │ A4 ║
╟────┼────┼────┼────╢
║ B1 │ B2 │ B3 │ B4 ║
║    │ B2 │    │    ║
║    │ B2 │    │    ║
╟────┼────┼────┼────╢
║ C1 │ C2 │ C3 │ C4 ║
╟────┼────┼────┼────╢
║ D1 │ D2 │ D3 │ D4 ║
╚════╧════╧════╧════╝
```

Transposed Tables
-----------------
Normally the "rows" are displayed left-to-right and "columns" are displayed up-to-down.  However, if you want to transpose
this and print "rows" up-to-down and "columns" left-to-right then that is easily done using the fourth (optional) argument
to ``generate_table``:

```Python
>>> print(generate_table(rows, cols, transpose=True))
╔══════╦════╤════╤════╤════╗
║ Col1 ║ A1 │ B1 │ C1 │ D1 ║
║ Col2 ║ A2 │ B2 │ C2 │ D2 ║
║      ║    │ B2 │    │    ║
║      ║    │ B2 │    │    ║
║ Col3 ║ A3 │ B3 │ C3 │ D3 ║
║ Col4 ║ A4 │ B4 │ C4 │ D4 ║
╚══════╩════╧════╧════╧════╝
``` 

Column Alignment
----------------
TODO

Number Formatting
-----------------
TODO

Color
-----
TODO
