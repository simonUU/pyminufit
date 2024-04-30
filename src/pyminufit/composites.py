"""Automatic combination of PDFs

This module handles the automatic combination of PDFs.
A combination can be a product or addition of two PDFs.

Also convolution is supported.

"""

from __future__ import annotations

from typing import Any, Optional, Tuple, Union

from iminuit import Minuit
from iminuit.cost import ExtendedUnbinnedNLL
from numpy.typing import ArrayLike

from pyminufit.observables import create_real_var

from .pdf import Pdf
from .utils import AttrDict


class AddPdf(Pdf):
    """Add PDF class, for generic addition of pdfs

        This class combines two PDF classes into an new PDF normed by normalisation factors.
        It is the generic way to fit multiple components in a fit.

        Examples:
            Two models of clas ``PDF`` can easily combined automatically by calling:

            .. code-block:: python

                add_pdf = pdf1 + pdf2

            If more than two models are to be combined:

            .. code-block:: python

                 add_pdf = AddPdf([pdf1, pdf2, pdf3])

        Attributes:
            pdfs (AttrDict): dict of pdfs in the object
            norms (AttrDict): dict of normalisations
            primary_pdf (Pdf): primary pdf
    def __init__(self, pdfs: Optional[List[Pdf]] = None, name: Optional[str] = None, **kwds) -> None:

        Todo:
            * Allow for absolute and relative normalisations.

    """

    def __init__(
        self, pdfs: Optional[list[Pdf]] = None, name: Optional[str] = None, **kwds: Any
    ) -> None:
        self.pdfs = AttrDict()
        self.primary_pdf: Optional[Pdf] = None
        self.norms = AttrDict()
        self._external_norms = AttrDict()

        if pdfs is not None:
            if name is None:
                name = "_plus_".join(pdf.name for pdf in pdfs)
        else:
            pdfs = []
            if name is None:
                name = "AddPdf"
        super().__init__(name=name, **kwds)

        for pdf in pdfs:
            self.add(pdf)

        self.use_extended = True

    def add(self, pdf: Pdf) -> None:
        """Add a PDF to the AddPdf object

        Args:
            pdf (Pdf): pdf to be added to the object

        """
        if not self.primary_pdf:
            self.primary_pdf = pdf

        # Check for duplicate names
        if pdf.name in self.pdfs:
            msg = f"PDF with name {pdf.name} already exists"
            raise ValueError(msg)

        self.pdfs[pdf.name] = pdf
        self.norms["n_" + pdf.name] = 1.0
        self.init_pdf()

    def constrain_norm(self, pdf: Union[Pdf, str], normalization: float) -> None:
        """Constrain a norm with an external normalisation

        Args:
            pdf (:obj:`PDF` or :obj:`str`): PDF object from the AddPdf or name of corresponding PDF
            normalization (:obj:`ROOT.RooAbsReal`): New normalisation to be used in the ROOT.RooAddPdf initialisation

        """
        assert isinstance(pdf, (Pdf, str)), "please specify pdf"
        if isinstance(pdf, Pdf):
            pdf = pdf.name
        assert pdf in self.pdfs, "Pdf not found"

        # assert isinstance(normalization, ROOT.RooAbsReal), "Please provide ROOT.RooAbsReal type as normalisation"

        self._external_norms[pdf] = normalization
        self.init_pdf()  # reset the pdf and change corresponding normalisation

    def init_pdf(self) -> None:
        """Initialises the PDF object

        This method is called when a new PDF is added to the object.

        """
        for pdf_name, pdf in self.pdfs.items():
            if pdf_name not in self._external_norms:
                norm_var = create_real_var(("n_" + pdf_name, 10, 0, 100000000))
            else:
                norm_var = self._external_norms[pdf_name]
            self.norms[pdf_name] = norm_var
            self.parameters["n_" + pdf_name] = norm_var
            self.observables.update(pdf.observables)

            for param_name, param in pdf.parameters.items():
                self.parameters[pdf_name + "_" + param_name] = param

    def _fit(self, data: ArrayLike, **kwds: Any) -> Minuit:
        self.cost = ExtendedUnbinnedNLL(data, self.density)
        m = Minuit(
            self.cost,
            **{k: v.value for k, v in self.parameters.items()},
            name=tuple(self.parameters.keys()),
        )
        self._set_limits(m)
        m.migrad(**kwds)
        m.hesse()
        return m

    def density(self, x, *args) -> Tuple[float, float]:  # type: ignore[no-untyped-def]
        kwargs = dict(zip(self.parameters.keys(), args))
        norm_names = ["n_" + pdf_name for pdf_name in self.pdfs]
        norm = sum([kwargs[n] for n in norm_names])
        component_sum = 0
        for pdf_name, pdf in self.pdfs.items():
            pdf_params_dict = {k: kwargs[pdf_name + "_" + k] for k in pdf.parameters}
            component_sum += kwargs["n_" + pdf_name] * pdf.pdf(x, **pdf_params_dict)
        return norm, component_sum

    def pdf(self, x: ArrayLike, *args, **kwds) -> ArrayLike:  # type: ignore[no-untyped-def]
        kwargs = {k: v.value for k, v in self.parameters.items()}
        norm, component_sum = self.density(x, *kwargs.values())
        return component_sum / norm
