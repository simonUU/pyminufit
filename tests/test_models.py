import pytest
from pyminufit.models import Gauss


def test_Gauss_fit():
    # Test case 1: Testing with default parameters
    gauss = Gauss(observable=(-1, 1))
    data = [0.5, 1.0, 1.5, 2.0, 2.5]
    result = gauss.fit(data)
    assert result.valid
    assert gauss.parameters["mean"].value == pytest.approx(1.5, abs=1e-0)
    assert gauss.parameters["sigma"].value == pytest.approx(0.5, abs=1e-0)

    # Test case 2: Testing with custom parameters
    gauss = Gauss(observable=("x", -1, 1), mean=(-2, -1, 0), sigma=(1, 2))
    data = [-1.0, 0.0, 1.0]
    result = gauss.fit(data)
    assert result.valid
    assert gauss.parameters["mean"].value == pytest.approx(0.0, abs=1e-0)
    assert gauss.parameters["sigma"].value == pytest.approx(1.0, abs=1e-0)
