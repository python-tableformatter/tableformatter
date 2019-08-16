# coding=utf-8
from typing import Union, Iterable, Callable, Optional, Tuple


# This whole try/except exists to make sure a Collection type exists for use with optional type hinting and isinstance
try:
    # Python 3.6+ should have Collection in the typing module
    from typing import Collection
except ImportError:
    from typing import Container, Generic, Sized, TypeVar

    # Python 3.5
    # noinspection PyAbstractClass
    class Collection(Generic[TypeVar('T_co', covariant=True)], Container, Sized, Iterable):
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
