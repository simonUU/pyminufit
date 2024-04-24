"""PDF base class"""

from __future__ import annotations

from typing import Any

from iminuit import Minuit
from numpy.typing import ArrayLike

from .observables import RealVar, create_real_var
from .utils import AttrDict, ClassLoggingMixin


class Pdf(ClassLoggingMixin):
    """PDF base class"""

    def __init__(self, name, observables=None, **kwds):
        """Initialise the Pdf"""
        super().__init__(**kwds)
        self.name = name
        self.observables = AttrDict()
        if observables:
            for observable in observables:
                self.add_observable(observable)
        self.parameters = AttrDict()
        self.parameters_names = AttrDict()
        self.pdf = None
        self._init_pdf()

    def _init_pdf(self) -> None:
        """Initiate attributes for parameters"""
        for p in self.parameters:
            self.__setattr__(p, self.parameters[p])

    def add_parameter(
        self, param_var, param_name=None, final_name=None, **kwds
    ) -> RealVar:
        if final_name is None:
            assert (
                param_name is not None
            ), "Please provide a final name for the parameter"
            name = self.name + "_" + param_name
        else:
            name = final_name

        param = create_real_var(param_var, name=name, **kwds)
        self.parameters[param_name] = param
        self.parameters_names[param_name] = name
        self.__setattr__(param_name, param)
        return self.parameters[param_name]

    def add_observable(self, observable_var, **kwds) -> RealVar:
        """Add an observable to the PDF"""
        if isinstance(observable_var, (list, tuple)) and not isinstance(
            observable_var[0], str
        ):
            self.warn("WARNING : choosing automatic variable name 'x'")

        observable = create_real_var(observable_var, **kwds)
        name = observable.name
        self.observables[name] = observable
        return self.observables[name]

    def fit(self, data: ArrayLike, *args, **kwds) -> Minuit:
        """Fit the PDF to the data"""
        self.logger.debug("Fitting")
        return self._fit(data, *args, **kwds)

    def _fit(self, *args, **kwds) -> Minuit:
        msg = "Please implement the fit method"
        raise NotImplementedError(msg)

    def _update_parameters(self, m: Minuit):
        for p in self.parameters:
            self.parameters[p].value = m.values[p]
            self.parameters[p].error = m.errors[p]
            self.__setattr__(p, self.parameters[p])

    def evaluate(self, x):
        msg = "Please implement the evaluate method"
        raise NotImplementedError(msg)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.evaluate(*args, **kwds)
