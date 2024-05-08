"""
Copyright (c) 2024 Simon. All rights reserved.

pyminufit: A great package.
"""

from __future__ import annotations

from .models import Chebyshev, Gauss, Normal
from .observables import RealVar, create_real_var
from .version import version as __version__

__all__ = ["Gauss", "Normal", "Chebyshev", "create_real_var", "RealVar", "__version__"]
