from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import matplotlib.pyplot as plt
import numpy as np
from numpy.typing import ArrayLike, NDArray

HATCHES = [
    "",
    "///",
    r"\\\ ",
    "xxx",
    "--",
    "++",
    "o",
    ".+",
    "xx",
    "//",
    "*",
    "O",
    ".",
]
DEFAULT_COLORS = [
    "#E24A33",
    "#348ABD",
    "#988ED5",
    "#777777",
    "#FBC15E",
    "#8EBA42",
    "#FFB5B8",
]


@dataclass
class Hist:
    """
    Represents a histogram.

    Attributes:
        n (int): The number of bins in the histogram.
        xe (numpy.ndarray): The bin edges of the histogram.

    Methods:
        __post_init__(self) -> None: Initializes the histogram object and calculates additional attributes.
    """

    n: int
    xe: NDArray

    def __post_init__(self) -> None:
        self.ne = self.n**0.5
        self.cx = 0.5 * (self.xe[1:] + self.xe[:-1])
        self.dx = np.diff(self.xe)
        self.xlim = (self.xe[0], self.xe[-1])


class Plotter:
    def __init__(
        self,
        model: Any,
        data: ArrayLike,
        nbins: Optional[int] = None,
        xrange: Optional[Tuple[float, float]] = None,
        ax: Optional[List[plt.Axes]] = None,
        cfg: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize the Plotter object.

        Args:
            model: The model used for fitting.
            data: The data to be plotted.
            nbins: The number of bins for the histogram. If not provided, it is calculated based on the data length.
            xrange: The range of the x-axis. If not provided, it is determined based on the minimum and maximum values of the data.
            ax: The list of matplotlib Axes objects to plot on. If not provided, a new Axes object will be created.
            cfg: Additional configuration options for the plot. If not provided, an empty dictionary is used.

        Returns:
            None
        """
        self.cfg = cfg or {}
        self.model = model
        self.data = data
        self.xrange = xrange or (np.min(data), np.max(data))
        self.nbins = nbins or int(2 * len(data) ** 0.333)
        self.h = Hist(*np.histogram(data, bins=self.nbins, range=self.xrange))
        self.scale = len(data) * self.h.dx[0]
        self.ax: List[plt.Axes] = ax or []
        self.parts: Dict[str, Callable[[], None]] = {
            "hist": self.plot_hist,
            "pdf": self.plot_pdf,
            "pull": self.plot_pull,
            "residuals": self.plot_residuals,
            "legend": self.plot_legend,
            "components": self.plot_components,
            "axes_labels": self.plot_axes_labels,
            "distribution": self.plot_distribution,
        }

    def setup_axis(
        self, ax: Optional[Union[plt.Axes, List[plt.Axes]]], components: List[str]
    ) -> List[plt.Axes]:
        if not ax:
            nx = 1
            gridspec_kw = None
            if components and ("pull" in components):
                nx = 2
                gridspec_kw = {"height_ratios": [4, 1]}
            _, ax = plt.subplots(
                nx,
                1,
                sharex=True,
                figsize=self.cfg.get("figsize", (4, 4)),
                gridspec_kw=gridspec_kw,
            )
            if nx > 1:
                ax = list(ax)
        if not isinstance(ax, list):
            ax = [ax]
        return ax  # type: ignore[no-any-return]

    def plot(
        self,
        components: Optional[List[str]] = None,
        filename: Optional[str] = None,
        *args: Any,
        **kwargs: Any,
    ) -> Plotter:
        if not components:
            # check if self.model has attribute pdfs
            if hasattr(self.model, "pdfs"):
                components = [
                    "hist",
                    "pdf",
                    "pull",
                    "components",
                    "legend",
                    "axes_labels",
                ]
            else:
                components = ["hist", "pdf", "axes_labels", "distribution"]
        self.ax = self.setup_axis(None, components)
        for c in components:
            self.parts[c]()
        if len(self.ax) > 1:
            plt.subplots_adjust(hspace=0)
        if filename:
            plt.savefig(filename, *args, **kwargs, bbox_inches="tight")
        return self

    def plot_hist(self) -> None:
        self.ax[0].errorbar(self.h.cx, self.h.n, self.h.ne, self.h.dx / 2.0, fmt=".k")
        self.ax[0].set_xlim(min(self.data), max(self.data))
        self.ax[0].set_ylim(0, None)

    def plot_pdf(self) -> None:
        xx = np.linspace(*self.h.xlim, 1000)
        self.ax[0].plot(xx, self.scale * self.model(xx), color="black")

    def plot_pull(self) -> None:
        yerr = self.h.ne
        yerr[yerr == 0] = np.inf
        pull = (self.h.n - self.scale * self.model(self.h.cx)) / yerr

        self.ax[1].bar(self.h.cx, pull, width=self.h.dx, alpha=0.5, color="gray")
        self.ax[1].hlines(0, *self.h.xlim, linestyles="dashed", color="black")
        self.ax[1].tick_params(which="both", top=True, right=True)
        self.ax[1].set_ylim(-2, 2)
        self.ax[1].set_yticks([-1, 1])

    def plot_residuals(self) -> None:
        self.ax[1].errorbar(
            self.h.cx,
            self.h.n - self.scale * self.model(self.h.cx),
            self.h.ne,
            fmt="ok",
        )
        self.ax[1].hlines(0, *self.h.xlim, linestyles="dashed", color="black")

    def plot_components(self) -> None:
        from pyminufit.composites import AddPdf

        if not isinstance(self.model, AddPdf):
            return
        ax = self.ax[0]

        for i, pdf_name in enumerate(self.model.pdfs):
            pdf = self.model.pdfs[pdf_name]

            pdf_norm = self.model.norms[pdf.name].value / sum(
                self.model.norms[pdf].value for pdf in self.model.pdfs
            )
            xx = np.linspace(*self.h.xlim, 1000)
            yy = self.scale * pdf_norm * pdf(xx)
            current_color = (
                ax._get_lines.get_next_color()
                if self.cfg.get("override_color", False)
                else DEFAULT_COLORS[i % len(DEFAULT_COLORS)]
            )
            ax.plot(xx, yy, color=current_color)
            ax.fill_between(
                xx,
                yy,
                alpha=0.5,
                hatch=HATCHES[i % len(HATCHES)],
                facecolor="none" if i > 0 else current_color,
                edgecolor=current_color,
                label=pdf.title,
            )

    def plot_legend(self) -> None:
        self.ax[0].legend(**self.cfg.get("legend", {}), frameon=False)

    def plot_axes_labels(self) -> None:
        binsize = self.h.dx[0]
        obs_name = self.model.observable.name
        obs_unit = self.model.observable.unit or ""
        per_bin = f"{binsize:.1g}"
        if obs_unit != "":
            per_bin = f" ( {per_bin} {obs_unit} )"
        self.ax[0].set_ylabel(f"Entries / {per_bin}")
        if len(self.ax) > 1:
            self.ax[1].set_ylabel("Pull")

        if len(obs_unit) > 0:
            obs_unit = f" [{obs_unit}]"
        self.ax[-1].set_xlabel(f"{obs_name}{obs_unit}")

    def plot_distribution(self) -> None:
        self.ax[0].plot(self.data, np.zeros_like(self.data), "|", alpha=0.1)
