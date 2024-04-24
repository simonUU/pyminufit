"""Fit models predefined"""

from __future__ import annotations

from iminuit import Minuit
from iminuit.cost import UnbinnedNLL
from scipy.stats import norm

from .pdf import Pdf


class Gauss(Pdf):
    """Standard gaussian"""

    def __init__(self, observable, mean=(-1, 0, 1), sigma=(0, 1), name="gauss", **kwds):
        super().__init__(name, **kwds)

        _ = self.add_observable(observable)

        mean = self.add_parameter(mean, "mean")
        sigma = self.add_parameter(sigma, "sigma")

    def _fit(self, data, *args, **kwds):
        cost = UnbinnedNLL(data, self._pdf)
        m = Minuit(
            cost,
            mean=self.parameters["mean"].value,
            sigma=self.parameters["sigma"].value,
        )
        # ToDo: set limits
        m.migrad(*args, **kwds)
        m.hesse()
        self._update_parameters(m)
        return m

    def _pdf(self, x, mean, sigma):
        return norm.pdf(x, mean, sigma)

    def evaluate(self, x):
        return self._pdf(
            x, self.parameters["mean"].value, self.parameters["sigma"].value
        )
