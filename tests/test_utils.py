# coding=utf-8
# flake8: noqa E302
"""
Unit testing of tableformatter utility functions.
"""
import pytest

from tableformatter.text_utils import _text_wrap, _translate_tabs, _printable_width


@pytest.fixture
def empty_text():
    return ''


@pytest.fixture
def sample_text():
    return 'FooBar'


@pytest.fixture
def long_text():
    return 'FooBarBaz'


@pytest.fixture
def tabbed_text():
    return 'Foo\tBar'


@pytest.fixture
def multiline_text():
    return 'FooBar\nBaz'


@pytest.fixture
def whitespace_text():
    return 'FooBar  \n    '


# Test text wrapping
def test_empty_wrap(empty_text):
    expected = []
    wrapped = _text_wrap(empty_text)
    assert expected == wrapped


def test_no_wrap(sample_text):
    expected = [sample_text]
    wrapped = _text_wrap(sample_text)
    assert expected == wrapped


def test_simple_wrap(sample_text):
    expected = ['Foo', 'Bar']
    wrapped = _text_wrap(sample_text, width=3)
    assert expected == wrapped


def test_double_wrap(long_text):
    expected = ['Foo', 'Bar', 'Baz']
    wrapped = _text_wrap(long_text, width=3)
    assert expected == wrapped


def test_multiline_no_wrap(multiline_text):
    expected = ['FooBar Baz']
    wrapped = _text_wrap(multiline_text)
    assert expected == wrapped


def test_multiline_with_wrap(multiline_text):
    expected = ['Foo', 'Bar', 'Baz']
    wrapped = _text_wrap(multiline_text, width=3)
    assert expected == wrapped


def test_trailing_whitespace_wrap(whitespace_text):
    expected = ['FooBar']
    wrapped = _text_wrap(whitespace_text)
    assert expected == wrapped


# Test tab translation and printable width calculation
def test_empty_translation(empty_text):
    expected = empty_text
    translated = _translate_tabs(empty_text)
    assert expected == translated


def test_empty_width(empty_text):
    assert _printable_width(empty_text) == len(empty_text)


def test_translation_no_tabs(sample_text):
    expected = sample_text
    translated = _translate_tabs(sample_text)
    assert expected == translated


def test_width_no_tabs(sample_text):
    assert _printable_width(sample_text) == len(sample_text)


def test_translation_with_tabs(tabbed_text):
    expected = 'Foo Bar'
    translated = _translate_tabs(tabbed_text)
    assert expected == translated
    assert expected != tabbed_text


def test_width_with_tabs(tabbed_text):
    expected = 'Foo Bar'
    assert _printable_width(tabbed_text) == len(expected)
