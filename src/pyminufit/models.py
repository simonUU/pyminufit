# -*- coding: utf-8 -*-
""" Fit models predefined

"""
from .pdf import Pdf
from scipy.stats import norm
from iminuit.cost import UnbinnedNLL
from iminuit import Minuit

class Gauss(Pdf):
    """ Standard gaussian

    """
    def __init__(self,
                 observable,
                 mean=(-1, 0, 1),
                 sigma=(0, 1),
                 name='gauss', **kwds):

        super(Gauss, self).__init__(name=name,  **kwds)

        x = self.add_observable(observable)

        mean = self.add_parameter(mean, "mean")
        sigma = self.add_parameter(sigma, "sigma")

    def _fit(self, data):
        cost = UnbinnedNLL(data, self._pdf)
        m = Minuit(cost, mean=self.mean.value, sigma=self.sigma.value)
        # ToDo: set limits
        m.migrad()
        m.hesse()
        self._update_parameters(m)
        return m
    
    def _pdf(self, x, mean, sigma):
        return norm.pdf(x, mean, sigma)

    def evaluate(self, x):
        return self._pdf(x, self.mean(), self.sigma())