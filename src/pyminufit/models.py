"""Fit models predefined"""

from __future__ import annotations

from typing import Any, Sequence

from iminuit import Minuit
from iminuit.cost import UnbinnedNLL
from numpy.typing import ArrayLike
from scipy.stats import norm

from .pdf import Pdf


class Gauss(Pdf):
    """Standard gaussian"""

    def __init__(
        self,
        observable: Sequence[Any],
        mean: Sequence[Any] = (-1, 0, 1),
        sigma: Sequence[Any] = (0, 1),
        name: str = "gauss",
        **kwds: Any,
    ):
        super().__init__(name, **kwds)

        self.add_observable(observable)
        self.add_parameter(mean, "mean")
        self.add_parameter(sigma, "sigma")

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
