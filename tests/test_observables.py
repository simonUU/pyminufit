from __future__ import annotations
import pytest
from pyminufit.observables import create_real_var


def test_create_real_var():
    # Test case 1: Testing with var=None
    result = create_real_var()
    assert result.name == None
    assert result.value is None
    assert result.lwb is None
    assert result.upb is None
    assert result.unit == ""

    # Test case 2: Testing with var=['x', -1, 1]
    result = create_real_var(var=["x", -1, 1])
    assert result.name == "x"
    assert result.value == 0
    assert result.lwb == -1
    assert result.upb == 1
    assert result.unit == ""

    # Test case 3: Testing with var=(-2, 0, 3)
    result = create_real_var(var=(-2, 0, 3))
    assert result.name == "x"
    assert result.value == 0
    assert result.lwb == -2
    assert result.upb == 3
    assert result.unit == ""

    # Test case 4: Testing with custom values
    result = create_real_var(name="y", lwb=-10, upb=10, value=5, unit="m")
    assert result.name == "y"
    assert result.value == 5
    assert result.lwb == -10
    assert result.upb == 10
    assert result.unit == "m"
    assert float(result) == 5
