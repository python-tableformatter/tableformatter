#!/usr/bin/python
# coding=utf-8
"""
Setuptools setup file, used to install or test 'tableformatter'
"""
from setuptools import setup

VERSION = '0.0.1'
DESCRIPTION = "python-tableformatter - Tabular data formatter allowing printing from both arbitrary tuples of strings or object inspection"
LONG_DESCRIPTION = """tableformatter is a tabular data formatter allowing printing from both arbitrary tuples of strings or object inspection.
It converts your data into a string form suitable for pretty-printing as a table.  The goal is to make it quick and easy
for developers to display tabular data in an aesthetically pleasing fashion.  It provides a simple public API, but allows
fine-grained control over almost every aspect of how the data is formatted.
"""

CLASSIFIERS = list(filter(None, map(str.strip,
"""
Environment :: Console
Operating System :: OS Independent
Intended Audience :: Developers
Intended Audience :: System Administrators
License :: OSI Approved :: MIT License
Programming Language :: Python
Programming Language :: Python :: 3
Programming Language :: Python :: 3.4
Programming Language :: Python :: 3.5
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: Implementation :: CPython
Topic :: Software Development :: Libraries :: Python Modules
""".splitlines())))

INSTALL_REQUIRES = ['colorama']

EXTRAS_REQUIRE = {
    # POSIX OSes also require wcwidth for correctly estimating the displayed width of unicode chars
    ":sys_platform!='win32'": ['wcwidth'],
    # Python 3.4 and earlier require contextlib2 for temporarily redirecting stderr and stdout
    ":python_version<'3.5'": ['typing'],
    # development only dependencies
    # install with 'pip install -e .[dev]'
    'dev': [
        'pytest', 'pytest-cov', 'tox', 'pylint', 'sphinx', 'sphinx-rtd-theme',
        'sphinx-autobuild', 'invoke', 'twine>=1.11',
    ]
}

setup(
    name="tableformatter",
    version=VERSION,
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    author='Eric Lin',
    author_email='anselor@gmail.com',
    url='https://github.com/python-tableformatter/tableformatter',
    license='MIT',
    platforms=['any'],
    py_modules = ['TableFormatter'],
    keywords='table tabular formatter',
    python_requires='>=3.4',
    install_requires=INSTALL_REQUIRES,
    extras_require=EXTRAS_REQUIRE,
)
