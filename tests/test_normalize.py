# coding=utf-8
# flake8: noqa E302
"""
Unit testing of tableformatter with simple cases
- with a list of tuples as table entries
- using a list of objects for the table entries
"""
import pytest

from tableformatter.normalize import infer_columns


def test_normalize_single_dict():
    sample = {'Albatross': 1,
              'Bat': 'bat',
              'Cheetah': 2}

    foo = infer_columns(sample)
    assert len(foo) == 3
