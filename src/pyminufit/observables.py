"""
Observables

"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class RealVar:
    """Real variable class"""

    name: str
    value: float
    error: Optional[float]
    lwb: Optional[float]
    upb: Optional[float]
    unit: Optional[str]

    def __float__(self) -> float:
        return float(self.value)

    def __call__(self) -> float:
        return float(self.value)

    def _repr_html_(self) -> str:
        return f"<b>{self.name}</b>: {self.value:.3g} ± {self.error:.3g} {self.unit}"


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
    var: Optional[Union[list, tuple]] = None,  # type: ignore[type-arg]
    name: str = "x",
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
    name_override = name
    if var:
        name, value, lwb, upb = extract_from_list(var)
    if name_override:
        name = name_override
    return RealVar(name, value, error, lwb, upb, unit)  # type: ignore[arg-type]
