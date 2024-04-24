"""Observables"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RealVar:
    name: str
    value: float
    error: float
    lwb: float
    upb: float
    unit: str
    reference_obj: None

    def __float__(self):
        return float(self.value)

    def __call__(self) -> float:
        return float(self.value)

    def _repr_html_(self):
        return f"<b>{self.name}</b>: {self.value:.3g} ± {self.error:.3g} {self.unit}"


def extract_from_list(var):
    """Extract name, min, mean and max from a list

    Args:
        var (list): List in a format like ['x', -1, 1] or (-2, 0, 3)

    Returns:
        name, value, min, max

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
    var=None, name="x", lwb=None, upb=None, value=None, unit="", error=None
) -> RealVar:
    """Create a RealVar object

    Args:
        var (list): List in a format like ['x', -1, 1] or (-2, 0, 3)
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
    return RealVar(name, value, error, lwb, upb, unit, None)