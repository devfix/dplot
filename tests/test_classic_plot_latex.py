import inspect

from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX, PATH_OUTPUT_DIR_TYPST
import numpy as np
from dplot import *


def test_classic_plot():
    title = inspect.stack()[0][3]
    fig = Figure(title, margin={'t': 3, 'b': 10, 'l': 12, 'r': 12}, background_color=Color.ALICEBLUE, legend_setup=LegendSetup(enable=False))
    ts = TickSetup(enable=True)
    fig.axes['b'] = AxisSetup('x', scale=1, tick=ts, label_shift=1)
    fig.axes['l'] = AxisSetup('y', scale=1, tick=ts, label_shift=1)

    xs = np.linspace(-2, 2, 41)
    fig.add('b', 'l', xs, np.pow(xs, 2), ls=LineSetup(Color.BLUE))

    path_latex, path_latex_pdf = LatexGenerator(fig).export(PATH_OUTPUT_DIR_LATEX)  # generate pdf via LaTex
    assert check_identical_pdf(path_latex_pdf)  # check that pdf looks as expected
