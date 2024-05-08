# -*- coding: utf-8 -*-
"""Simple fit to a gaussian distribution

In this example a fit is performed to a simple gaussion distribution.

Observables can be initialised by a list with the column name / variable name as first argument, followed
by the range and/or with the initial value and range:
x = ('x', -3, 3)
x = ('mass', -3, 0.02, 3)

Parameters are initialised with a tuple: sigma=(0,1) or again including a starting parameter: sigma=(0.01, 0, 1)
The order here is not important.

"""

import pyminufit as mnf
import numpy as np


data = np.append(
    np.random.random_sample(1000) * 10 + 745, np.random.normal(750, 1, 1000)
)

x = mnf.create_real_var(("mass", 745, 755), unit="GeV")

pdf_sig = mnf.Gauss(x, mean=(745, 755), sigma=(0.1, 1, 2), title="Signal")
pdf_bkg = mnf.Chebyshev(x, order=2, title="Background")

pdf = pdf_sig + pdf_bkg

pdf.fit(data)
pdf.plot(data, "02_add_pdf.png", dpi=150)
pdf.get()
