from __future__ import annotations

import pytest

from pyminufit.utils import AttrDict, is_iterable


def test_is_iterable():
    assert is_iterable([])
    assert is_iterable((1, 2, 3))
    assert is_iterable("hello")
    assert not is_iterable(123)
    assert not is_iterable(None)


def test_AttrDict():
    data = {"a": 1, "b": 2, "c": 3}
    attr_dict = AttrDict(data)

    # Test item lookup
    assert attr_dict["a"] == 1
    assert attr_dict["b"] == 2
    assert attr_dict["c"] == 3

    # Test attribute lookup
    assert attr_dict.a == 1
    assert attr_dict.b == 2
    assert attr_dict.c == 3

    # Test modifying item
    attr_dict["a"] = 10
    assert attr_dict.a == 10

    # Test modifying attribute
    attr_dict.b = 20
    assert attr_dict["b"] == 20

    # Test adding new item
    attr_dict.d = 30
    assert attr_dict["d"] == 30
    assert attr_dict.d == 30

    # Test deleting item
    del attr_dict["c"]
    with pytest.raises(KeyError):
        attr_dict["c"]

    # Test deleting attribute
    del attr_dict.b
    with pytest.raises(AttributeError):
        attr_dict.b
