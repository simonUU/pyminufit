"""Fit models predefined"""

from __future__ import annotations

from typing import Any, Dict, Sequence, Union

import numpy as np
from iminuit import Minuit
from iminuit.cost import UnbinnedNLL
from numpy.polynomial.chebyshev import chebval
from numpy.typing import ArrayLike
from scipy.stats import norm

from .observables import RealVar
from .pdf import Pdf

__all__ = ["Gauss", "Normal", "Chebyshev"]


class Gauss(Pdf):
    """Standard gaussian"""

    def __init__(
        self,
        observable: Union[Sequence[Any], RealVar],
        mean: Union[Sequence[Any], RealVar] = (-1, 0, 1),
        sigma: Union[Sequence[Any], RealVar] = (0, 1),
        name: str = "gauss",
        *args: Any,
        **kwds: Any,
    ):
        super().__init__(name, *args, **kwds)

        self.add_observable(observable)
        self.add_parameter(mean, "mean")
        self.add_parameter(sigma, "sigma")
        self._init_pdf()

    def _fit(self, data: ArrayLike, **kwds: Any) -> Minuit:
        self.cost = UnbinnedNLL(data, self.pdf)
        m = Minuit(
            self.cost,
            mean=self.parameters["mean"].value,
            sigma=self.parameters["sigma"].value,
        )
        self._set_limits(m)
        m.migrad(**kwds)
        m.hesse()
        self._update_parameters(m)
        return m

    def pdf(self, x, mean, sigma):  # type: ignore[no-untyped-def]
        return norm.pdf(x, mean, sigma)


# Add alias
Normal = Gauss


class Chebyshev(Pdf):
    """Chebyshev"""

    def __init__(
        self,
        observable: Union[Sequence[Any], RealVar],
        order: int = 2,
        name: str = "chebyshev",
        do_normalize: bool = True,
        *args: Any,
        **kwds: Any,
    ):
        super().__init__(name, *args, **kwds)
        self.do_normalize = do_normalize
        self.add_observable(observable)
        for i in range(order):
            self.add_parameter((-1, 1), f"c{i}")
        self._init_pdf()

    def pdf(self, x, *args, **kwargs: Dict[str, Any]):  # type: ignore[no-untyped-def]
        coeffs = args if args else tuple(kwargs.values())

        c = np.array(list(coeffs))
        norm = 1.0

        x_range = np.linspace(self.observable.lwb, self.observable.upb, 1000)
        y_range = chebval(x_range, c)
        shift = -1 * min(np.min(y_range), 0)
        y_range += shift

        if self.do_normalize:
            # integrated_c = chebint(c, m=1)  # type: ignore[no-untyped-call]
            # norm = chebval(self.observable.upb, integrated_c) - chebval(self.observable.lwb, integrated_c)  # type: ignore[no-untyped-call]
            norm = np.trapz(y_range, x_range)  # integrate over the range
            if np.isnan(norm) or norm == 0:
                norm = 1.0

        y = chebval(x, c) + shift
        return y / norm

    def _fit(self, data: ArrayLike, **kwds: Any) -> Minuit:
        self.cost = UnbinnedNLL(data, self.pdf)
        m = Minuit(
            self.cost,
            **{k: v.value for k, v in self.parameters.items()},
            name=tuple(self.parameters.keys()),
        )
        self._set_limits(m)
        m.migrad(**kwds)
        m.hesse()
        self._update_parameters(m)
        return m
