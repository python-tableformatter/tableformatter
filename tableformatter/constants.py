# coding=utf-8
"""Tableformatter constants"""
from .grids import AlternatingRowGrid, Grid

# Global constant for default grid sytle
DEFAULT_GRID = AlternatingRowGrid()


def set_default_grid(grid: Grid) -> None:
    """Set the global constant for default grid style."""
    global DEFAULT_GRID
    if grid is not None:
        DEFAULT_GRID = grid
