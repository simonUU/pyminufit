"""PDF base class"""

from __future__ import annotations

from typing import Any, Dict, Optional

from iminuit import Minuit
from numpy.typing import ArrayLike

from .observables import RealVar, create_real_var
from .plotting import Plotter
from .utils import AttrDict, ClassLoggingMixin


class Pdf(ClassLoggingMixin):
    """PDF base class"""

    def __init__(
        self,
        name: str,
        observables: Optional[Any] = None,
        title: Optional[str] = None,
        **kwds: Any,
    ) -> None:
        """
        Initialize a PDF object.

        Args:
            name (str): The name of the PDF.
            observables (Optional[Any]): A list of observables.
            title (Optional[str]): The title of the PDF. If not provided, it defaults to the name.
            **kwds (Any): Additional keyword arguments.

        """
        super().__init__(**kwds)
        self.name = name
        self.title = title or name
        self.observables = AttrDict()
        if observables:
            for observable in observables:
                self.add_observable(observable)
        self.parameters = AttrDict()
        self.parameters_names = AttrDict()
        self.cost = None
        self._init_pdf()

    def _init_pdf(self) -> None:
        """Initiate attributes for parameters"""
        for p in self.parameters:
            setattr(self, p, self.parameters[p])

    def add_parameter(
        self,
        param_var: Any,
        param_name: Optional[str] = None,
        final_name: Optional[str] = None,
        **kwds: Any,
    ) -> RealVar:
        """
        Adds a parameter to the PDF object.

        Args:
            param_var (Any): The value of the parameter.
            param_name (Optional[str]): The name of the parameter. If not provided, a final name must be provided.
            final_name (Optional[str]): The final name of the parameter. If provided, it will be used as the name instead of param_name.
            **kwds (Any): Additional keyword arguments to be passed to create_real_var.

        Returns:
            RealVar: The added parameter.

        """
        if final_name is None:
            assert (
                param_name is not None
            ), "Please provide a final name for the parameter"
            name = self.name + "_" + param_name
        else:
            name = final_name
        assert isinstance(param_name, str), "Please provide a name for the parameter"
        param = create_real_var(param_var, name=name, **kwds)
        self.parameters[param_name] = param
        self.parameters_names[param_name] = name
        setattr(self, param_name, param)
        return self.parameters[param_name]  # type: ignore[no-any-return]

    @property
    def observable(self) -> RealVar:
        """Return the first observable"""
        if len(self.observables) == 0:
            msg = "No observables defined"
            raise ValueError(msg)
        if len(self.observables) > 1:
            self.warn("Multiple observables defined, returning the first one")
        return next(iter(self.observables.values()))  # type: ignore[no-any-return]

    def add_observable(self, observable_var: Any, **kwds: Any) -> RealVar:
        """Add an observable to the PDF"""
        if isinstance(observable_var, (list, tuple)) and not isinstance(
            observable_var[0], str
        ):
            self.warn("WARNING : choosing automatic variable name 'x'")

        observable = create_real_var(observable_var, **kwds)
        name = observable.name
        self.observables[name] = observable
        return self.observables[name]  # type: ignore[no-any-return]

    def fit(self, data: ArrayLike, **kwds: Any) -> Minuit:
        """Fit the PDF to the data"""
        self.logger.debug("Fitting")
        fit_res = self._fit(data, **kwds)
        self._update_parameters(fit_res)
        return fit_res

    def _fit(self, data: ArrayLike, **kwds: Any) -> Minuit:
        """Fit logic implemented in the models"""
        # pylint: disable=unused-argument
        msg = "Please implement the fit method"
        raise NotImplementedError(msg)

    def _update_parameters(self, m: Minuit) -> None:
        for p in self.parameters:
            self.parameters[p].value = m.values[p]
            self.parameters[p].error = m.errors[p]
            setattr(self, p, self.parameters[p])

    def _set_limits(self, m: Minuit) -> None:
        for p in self.parameters:
            m.limits[p] = (self.parameters[p].lwb, self.parameters[p].upb)

    def pdf(self, x: ArrayLike, *args, **kwds) -> ArrayLike:  # type: ignore[no-untyped-def]
        """PDF logic implemented in the models"""
        # pylint: disable=unused-argument
        return x

    def evaluate(self, x: ArrayLike) -> ArrayLike:
        """
        Evaluates the probability density function (PDF) at the given values of x.
        Args:
            x (ArrayLike): The values at which to evaluate the PDF.
        Returns:
            ArrayLike: The values of the PDF at the given values of x.
        """
        parameter_values = {p: self.parameters[p].value for p in self.parameters}
        return self.pdf(x, **parameter_values)

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        return self.evaluate(*args, **kwds)

    def __add__(self, other: Pdf) -> Pdf:
        from .composites import AddPdf

        return AddPdf([self, other])

    def plot(
        self,
        data: ArrayLike,
        filename: Optional[str] = None,
        cfg: Optional[Dict[str, Any]] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Plotter:
        """Plot the PDF"""
        return Plotter(self, data, cfg=cfg).plot(None, filename, *args, **kwargs)

    def get(self, parameter: Optional[str] = None, as_ufloat: bool = False) -> Any:
        """Get one of the fitted parameter or print all if None is set

        Args:
            parameter (str): name of the parameter
            as_ufloat (bool, optional): If true return ufloat object, else tuple

        Returns:
            :obj:`tuple` or :obj:`ufloat` mean and error of parameter

        """

        if parameter is None:
            for m in self.parameters:
                self.info(f"{m:18} ==> {self._get_parameter(m, True)}")
        else:
            return self._get_parameter(parameter, as_ufloat)
        return self.parameters

    def _get_parameter(self, param: str, as_ufloat: bool = False) -> Any:
        """Internal getter for parameter values

        Args:
            param: Parameter name
            as_ufloat: Return ufolat object

        Returns:
            :obj:`tuple` or :obj:`ufloat` mean and error of parameter
        """
        mes = self.parameters[param]
        val = mes.value

        # Now catch RooFormulaVar
        try:
            err = mes.error
        except AttributeError:
            err = 0
        if not as_ufloat:
            return val, err
        try:
            from uncertainties import ufloat

            return ufloat(val, err)
        except ImportError:
            return val, err

    def __getitem__(self, parameter_name: str) -> Any:
        return self._get_parameter(parameter_name)
