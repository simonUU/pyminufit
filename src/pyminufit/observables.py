"""
Observables

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional, Union


@dataclass
class RealVar:
    """
    Represents a real-valued variable with associated properties.

    Attributes:
        name (str): The name of the variable.
        value (float): The value of the variable.
        error (Optional[float]): The error associated with the variable (if available).
        lwb (Optional[float]): The lower bound of the variable (if available).
        upb (Optional[float]): The upper bound of the variable (if available).
        unit (Optional[str]): The unit of the variable (if available).
        is_constant (bool): Indicates whether the variable is constant or not.

    Methods:
        __float__(): Returns the value of the variable as a float.
        __call__(): Returns the value of the variable as a float.
        _repr_html_(): Returns an HTML representation of the variable.

    """

    name: str
    value: float
    error: Optional[float]
    lwb: Optional[float]
    upb: Optional[float]
    unit: Optional[str]
    is_constant: bool = False

    def __float__(self) -> float:
        return float(self.value)

    def __call__(self) -> float:
        return float(self.value)

    def _repr_html_(self) -> str:
        val = f"<b>{self.name}</b>: {self.value:.3g}"
        val += f" ± {self.error:.3g}" if self.error else ""
        return val + f" {self.unit}"


def extract_from_list(var: Union[list, tuple]) -> tuple:  # type: ignore[type-arg]
    """Extract name, min, mean and max from a list

    Args:
        var (list or tuple): List in a format like ['x', -1, 1] or (-2, 0, 3)

    Returns:
        Tuple containing name, value, min, max

    """
    var = list(var)
    val = lwb = upb = None
    name = "x"

    assert len(var) >= 2, "Please use a format like ['x', -1, 1] or (-2, 0, 3)"

    if isinstance(var[0], str):
        name = var[0]
        var = var[1:]
    var = sorted(var)
    if len(var) == 2:
        lwb, upb = var
        val = lwb + upb
        val /= 2.0
    if len(var) == 3:
        lwb, val, upb = var

    return name, val, lwb, upb


def create_real_var(
    var: Optional[Any] = None,
    name: Optional[str] = None,
    lwb: Optional[float] = None,
    upb: Optional[float] = None,
    value: Optional[float] = None,
    unit: str = "",
    error: Optional[float] = None,
) -> RealVar:
    """Create a RealVar object

    Args:
        var (list or tuple): List in a format like ['x', -1, 1] or (-2, 0, 3)
        name (str): Name of the variable
        lwb (float): Lower bound
        upb (float): Upper bound
        value (float): Value
        unit (str): Unit

    Returns:
        RealVar object

    """
    if isinstance(var, RealVar):
        return var

    name_override = name
    if var:
        override_bounds = False
        if isinstance(var, float):
            override_bounds = True
            var = (var, var, var)
        name, value, lwb, upb = extract_from_list(var)
        if override_bounds:
            lwb = upb = None
    if name_override:
        name = name_override
    return RealVar(name, value, error, lwb, upb, unit)  # type: ignore[arg-type]
