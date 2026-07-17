import inspect
from tests.tools import check_identical_pdf, PATH_OUTPUT_DIR_LATEX
import numpy as np
from dplot import *


def test_classic_plot():
    title = inspect.stack()[0][3]
    fig = Figure(title, margin={'t': 0, 'b': 0, 'l': 0, 'r': 0}, background_color=Color.ALICEBLUE, legend_setup=LegendSetup(enable=False))
    ts = TickSetup(enable=True)
    fig.axes['b'] = AxisSetup('x', scale=1, tick=ts, label_shift=1)
    fig.axes['l'] = AxisSetup('y', scale=1, tick=ts, label_shift=1)

    xs = np.linspace(-2, 2, 41)
    fig.add('b', 'l', xs, np.pow(xs, 2), ls=LineSetup(Color.BLUE))

    path_latex, path_pdf = LatexGenerator(fig).export(PATH_OUTPUT_DIR_LATEX)
    assert check_identical_pdf(path_pdf)
    # TypstGenerator(fig).export(PATH_OUTPUT_DIR_TYPST)
